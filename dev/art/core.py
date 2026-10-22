"""Mesh building, the texture atlas, the game-file writers and a small software
renderer that draws a model the way the game's camera sees a tile.

Conventions (the same ones Jamie's Fortune's cabinet uses, which is known to
load in the game): metres, Y up, the front of a model is +Z, the model stands
on the middle of its tile (x = z = 0 is the tile centre, y = 0 the floor).
"""
import io, math, struct
import numpy as np
from PIL import Image

# ============================================================================ atlas
class Atlas:
    """Shelf-packed texture atlas. Each named region is painted as its own
    image and pasted with a few pixels of edge bleed so neighbours never show
    through at the seams."""
    BLEED = 3

    def __init__(self, size=1024, background=(60, 52, 44, 255)):
        self.size = size
        self.img = Image.new('RGBA', (size, size), background)
        self.R = {}
        self._x, self._y, self._rowh = 0, 0, 0
        self._pending = {}

    def add(self, name, image):
        """Queues a region; finish() places them all (tallest first)."""
        if name in self._pending or name in self.R:
            raise ValueError('duplicate atlas region ' + name)
        self._pending[name] = image.convert('RGBA')

    def finish(self):
        b = self.BLEED
        for name, image in sorted(self._pending.items(), key=lambda kv: (-kv[1].height, -kv[1].width, kv[0])):
            w, h = image.size
            if self._x + w + 2 * b > self.size:
                self._x = 0
                self._y += self._rowh
                self._rowh = 0
            if self._y + h + 2 * b > self.size:
                raise ValueError('atlas is full at ' + name)
            x, y = self._x + b, self._y + b
            # edge bleed: paste a stretched copy first, then the real pixels
            self.img.paste(image.resize((w + 2 * b, h + 2 * b), Image.NEAREST), (x - b, y - b))
            opaque = image.copy(); opaque.putalpha(255)
            self.img.paste(opaque, (x, y))
            self.R[name] = (x, y, w, h)
            self._x += w + 2 * b
            self._rowh = max(self._rowh, h + 2 * b)
        self._pending = {}
        self.used = self._y + self._rowh
        return self

    def uv(self, name, sub=(0, 0, 1, 1), flip=False, rot=0, inset=0.75):
        """UVs for a quad given as (bottom-left, bottom-right, top-right, top-left).
        sub = (u0, v0, u1, v1) inside the region, v measured from the TOP of the picture.
        rot turns the picture on the quad in quarter turns."""
        x, y, w, h = self.R[name]
        x0 = x + inset + (w - 2 * inset) * sub[0]; x1 = x + inset + (w - 2 * inset) * sub[2]
        y0 = y + inset + (h - 2 * inset) * sub[1]; y1 = y + inset + (h - 2 * inset) * sub[3]
        A = float(self.size)
        u0, u1, v0, v1 = x0 / A, x1 / A, y0 / A, y1 / A
        if flip: u0, u1 = u1, u0
        c = [(u0, v1), (u1, v1), (u1, v0), (u0, v0)]
        r = rot % 4
        return c[r:] + c[:r]

    def point(self, name, u, v):
        x, y, w, h = self.R[name]
        return ((x + 0.75 + (w - 1.5) * u) / self.size, (y + 0.75 + (h - 1.5) * v) / self.size)


# ============================================================================ mesh
def _rot(axis, deg):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    if axis == 'x': return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    if axis == 'y': return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


class Mesh:
    BACK_GAP = 0.008

    def __init__(self):
        self.v, self.n, self.t, self.tri = [], [], [], []

    # ---- raw faces
    def quad(self, pts, uvs, two_sided=False, normals=None):
        """pts counter-clockwise seen from outside (right-handed, Y up)."""
        p = [np.array(q, dtype=float) for q in pts]
        n = np.cross(p[1] - p[0], p[3] - p[0])
        if np.linalg.norm(n) < 1e-12:
            n = np.cross(p[2] - p[1], p[0] - p[1])
        n = n / (np.linalg.norm(n) or 1)
        b = len(self.v)
        for i, (q, uv) in enumerate(zip(p, uvs)):
            self.v.append(q); self.n.append(np.array(normals[i], dtype=float) if normals else n); self.t.append(tuple(uv))
        self.tri += [(b, b + 1, b + 2), (b, b + 2, b + 3)]
        if two_sided:
            # The back is its own face a few millimetres behind, never the same
            # surface seen from the other side: coplanar faces flicker.
            b = len(self.v)
            for i, (q, uv) in enumerate(zip(p, uvs)):
                self.v.append(q - n * self.BACK_GAP); self.n.append(-(np.array(normals[i], dtype=float) if normals else n)); self.t.append(tuple(uv))
            self.tri += [(b, b + 2, b + 1), (b, b + 3, b + 2)]

    def triangle(self, pts, uvs, two_sided=False):
        p = [np.array(q, dtype=float) for q in pts]
        n = np.cross(p[1] - p[0], p[2] - p[0]); n = n / (np.linalg.norm(n) or 1)
        b = len(self.v)
        for q, uv in zip(p, uvs):
            self.v.append(q); self.n.append(n); self.t.append(tuple(uv))
        self.tri.append((b, b + 1, b + 2))
        if two_sided:
            b = len(self.v)
            for q, uv in zip(p, uvs):
                self.v.append(q - n * self.BACK_GAP); self.n.append(-n); self.t.append(tuple(uv))
            self.tri.append((b, b + 2, b + 1))

    # ---- solids
    def box(self, x0, x1, y0, y1, z0, z1, side, top=None, front=None, back=None, left=None, right=None, bottom=None):
        """Axis-aligned box. Each face takes UVs (bl, br, tr, tl); `side` is the default."""
        top = top or side; front = front or side; back = back or side; left = left or side; right = right or side
        self.quad([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], front)
        self.quad([(x1, y0, z0), (x0, y0, z0), (x0, y1, z0), (x1, y1, z0)], back)
        self.quad([(x1, y0, z1), (x1, y0, z0), (x1, y1, z0), (x1, y1, z1)], right)
        self.quad([(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)], left)
        self.quad([(x0, y1, z1), (x1, y1, z1), (x1, y1, z0), (x0, y1, z0)], top)
        if bottom: self.quad([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], bottom)
        self._outward(len(self.tri) - (12 if bottom else 10), ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))

    def _outward(self, first, centre, axis=None):
        """Faces of a solid just built must wind so they face away from its middle
        (measured from its axis for a tube): the game draws the counter-clockwise side."""
        centre = np.array(centre, dtype=float)
        for (a, b, c) in self.tri[first:]:
            pa, pb, pc = self.v[a], self.v[b], self.v[c]
            g = np.cross(pb - pa, pc - pa)
            out = (pa + pb + pc) / 3 - centre
            if axis is not None:
                out = out - axis * float(out @ axis)
            if float(g @ out) <= 0:
                raise ValueError('a face of a solid winds inwards near %s' % np.round(pa, 3))

    def bar(self, a, b, w, d, side, up=(0, 1, 0)):
        """A straight beam of section w x d from point a to point b."""
        a = np.array(a, dtype=float); b = np.array(b, dtype=float)
        ax = b - a; L = np.linalg.norm(ax); ax = ax / L
        up = np.array(up, dtype=float)
        if abs(ax @ up) > 0.95: up = np.array([1.0, 0, 0])
        s = np.cross(ax, up); s = s / np.linalg.norm(s); u = np.cross(s, ax)
        hs, hu = s * w / 2, u * d / 2
        first = len(self.tri)
        c0 = [a - hs - hu, a + hs - hu, a + hs + hu, a - hs + hu]
        c1 = [q + ax * L for q in c0]
        for i in range(4):
            j = (i + 1) % 4
            self.quad([c0[j], c0[i], c1[i], c1[j]], side)
        self.quad([c0[0], c0[1], c0[2], c0[3]], side)
        self.quad([c1[3], c1[2], c1[1], c1[0]], side)
        self._outward(first, (a + b) / 2)

    def tube(self, base, r0, r1, h, n, side, top=None, bottom=None, smooth=True, axis=(0, 1, 0), start=0.0, wrap=1.0):
        """Cylinder / cone frustum from `base` along `axis`. `side` UVs are wrapped
        `wrap` times round; `top`/`bottom` are (atlas, name) or UV quads mapped as a disc."""
        base = np.array(base, dtype=float); ax = np.array(axis, dtype=float); ax = ax / np.linalg.norm(ax)
        ref = np.array([0, 0, 1.0]) if abs(ax[2]) < 0.9 else np.array([1.0, 0, 0])
        ex = np.cross(ax, ref); ex = ex / np.linalg.norm(ex); ez = np.cross(ex, ax)     # axis +Y: ex = +X, ez = +Z
        (u0, v1), (u1, _), (_, v0), _ = side[0], side[1], side[2], side[3]
        ring = lambda r, k: ex * (r * math.sin(2 * math.pi * (k / n + start))) + ez * (r * math.cos(2 * math.pi * (k / n + start)))
        slope = (r0 - r1) / (h or 1)
        first = len(self.tri)
        for k in range(n):
            a0, a1 = ring(r0, k), ring(r0, k + 1)
            b0, b1 = ring(r1, k), ring(r1, k + 1)
            f0 = (k * wrap / n) % 1.0 if wrap != 1 else k / n
            if f0 + wrap / n > 1.0 + 1e-9:                # never run off the edge of the picture
                f0 = 1.0 - wrap / n
            ua = u0 + (u1 - u0) * f0
            ub = ua + (u1 - u0) * wrap / n
            norms = None
            if smooth:
                d0 = ring(1.0, k) + ax * slope; d1 = ring(1.0, k + 1) + ax * slope
                d0 = d0 / np.linalg.norm(d0); d1 = d1 / np.linalg.norm(d1)
                norms = [d0, d1, d1, d0]
            self.quad([base + a0, base + a1, base + ax * h + b1, base + ax * h + b0], [(ua, v1), (ub, v1), (ub, v0), (ua, v0)], normals=norms)
        self._outward(first, base + ax * (h / 2), axis=ax)
        if top is not None and r1 > 1e-6:
            self.disc(base + ax * h, r1, n, top, axis=ax, start=start)
        if bottom is not None and r0 > 1e-6:
            self.disc(base, r0, n, bottom, axis=-ax, start=start)

    def disc(self, centre, r, n, uvq, axis=(0, 1, 0), start=0.0, two_sided=False, rx=None):
        """Flat n-gon; `uvq` is a UV quad and the picture is mapped across the disc.
        With axis = +Y the picture's top edge points to -Z (away from the front)."""
        c = np.array(centre, dtype=float); ax = np.array(axis, dtype=float); ax = ax / np.linalg.norm(ax)
        if abs(ax[1]) > 0.9:
            ex = np.array([1.0, 0, 0]); ez = np.cross(ex, ax)       # ez = +Z for axis +Y -> flip so v up = -Z
            ez = -ez if ax[1] > 0 else ez
        else:
            ref = np.array([0, 1.0, 0]); ex = np.cross(ref, ax); ex = ex / np.linalg.norm(ex); ez = np.cross(ax, ex)
        (u0, v1), (u1, _), (_, v0), _ = uvq[0], uvq[1], uvq[2], uvq[3]
        uc, vc = (u0 + u1) / 2, (v0 + v1) / 2
        def pt(k):
            a = 2 * math.pi * (k / n + start)
            dx, dz = math.sin(a), math.cos(a)
            p = c + ex * (r * dx) + ez * ((rx or r) * dz)
            return p, (uc + (u1 - u0) / 2 * dx, vc - (v1 - v0) / 2 * dz)
        for k in range(n):
            p0, t0 = pt(k); p1, t1 = pt(k + 1)
            tri = [c, p0, p1]; uv = [(uc, vc), t0, t1]
            nrm = np.cross(p0 - c, p1 - c)
            if nrm @ ax < 0: tri = [c, p1, p0]; uv = [(uc, vc), t1, t0]
            self.triangle(tri, uv, two_sided=two_sided)

    def cone_canopy(self, apex, r, drop, n, panel_uvs, underside=None, start=0.0, sag=0.0):
        """Umbrella canopy: n triangular panels from the apex down to a rim."""
        apex = np.array(apex, dtype=float)
        def rim(k):
            a = 2 * math.pi * (k / n + start)
            return apex + np.array([r * math.sin(a), -drop, r * math.cos(a)])
        for k in range(n):
            p0, p1 = rim(k), rim(k + 1)
            uvq = panel_uvs[k % len(panel_uvs)]
            (u0, v1), (u1, _), (_, v0), _ = uvq
            mid = (p0 + p1) / 2 + np.array([0, -sag, 0])
            um = (u0 + u1) / 2
            # two triangles per panel so the rim can sag between the ribs
            self.triangle([apex, p0, mid], [(um, v0), (u0, v1), (um, v1)])
            self.triangle([apex, mid, p1], [(um, v0), (um, v1), (u1, v1)])
            if underside:
                (a0, b1), (a1, _), (_, b0), _ = underside
                am = (a0 + a1) / 2
                lo = np.array([0, -1.5 * self.BACK_GAP, 0])
                self.triangle([apex + lo, mid + lo, p0 + lo], [(am, b0), (am, b1), (a0, b1)])
                self.triangle([apex + lo, p1 + lo, mid + lo], [(am, b0), (a1, b1), (am, b1)])

    # ---- composition
    def merge(self, other, rotate=(), translate=(0, 0, 0), scale=1.0):
        """Adds another mesh, turned (list of (axis, degrees), applied in order) then moved."""
        M = np.eye(3)
        for axis, deg in rotate:
            M = _rot(axis, deg) @ M
        t = np.array(translate, dtype=float)
        b = len(self.v)
        sc = np.array(scale if isinstance(scale, (tuple, list)) else (scale, scale, scale), dtype=float)
        for q, n, uv in zip(other.v, other.n, other.t):
            self.v.append(M @ (np.array(q) * sc) + t)
            nn = M @ (np.array(n) / sc); self.n.append(nn / (np.linalg.norm(nn) or 1))
            self.t.append(uv)
        self.tri += [(a + b, c + b, d + b) for (a, c, d) in other.tri]
        return self

    def bounds(self):
        V = np.array(self.v)
        return V.min(axis=0), V.max(axis=0)

    def check(self, name=''):
        """Every triangle must wind counter-clockwise seen from the side its normals
        point to (the game draws that side), be a real triangle, and no two faces may
        lie on top of each other facing opposite ways."""
        for (u, v) in self.t:
            if not (0.0 <= u <= 1.0 and 0.0 <= v <= 1.0):
                raise ValueError('%s: texture coordinate outside the atlas' % name)
        seen = {}
        for (a, b, c) in self.tri:
            pa, pb, pc = self.v[a], self.v[b], self.v[c]
            g = np.cross(pb - pa, pc - pa)
            area = np.linalg.norm(g)
            if area < 1e-10:
                raise ValueError('%s: degenerate triangle' % name)
            g = g / area
            for k in (a, b, c):
                if float(g @ self.n[k]) <= 0.05:
                    raise ValueError('%s: a face winds against its normal near %s' % (name, np.round(pa, 3)))
            key = tuple(sorted(tuple(np.round(q, 4)) for q in (pa, pb, pc)))
            sign = tuple(np.round(g, 3))
            if key in seen and seen[key] != sign:
                raise ValueError('%s: two faces share the same surface near %s' % (name, np.round(pa, 3)))
            seen[key] = sign
        return self


# ============================================================================ binary FBX 7.4 writer
class _A:
    def __init__(self, code, values): self.code, self.values = code, values
class _I64(int): pass
class _B(int): pass

def _prop(v):
    if isinstance(v, _A):
        fmt = {'d': 'd', 'i': 'i'}[v.code]
        raw = struct.pack('<%d%s' % (len(v.values), fmt), *v.values)
        return v.code.encode() + struct.pack('<III', len(v.values), 0, len(raw)) + raw
    if isinstance(v, _B): return b'C' + struct.pack('<b', int(v))
    if isinstance(v, _I64): return b'L' + struct.pack('<q', int(v))
    if isinstance(v, bool): return b'C' + struct.pack('<b', 1 if v else 0)
    if isinstance(v, int): return b'I' + struct.pack('<i', v)
    if isinstance(v, float): return b'D' + struct.pack('<d', v)
    if isinstance(v, bytes): return b'R' + struct.pack('<I', len(v)) + v
    b = v.encode('latin1'); return b'S' + struct.pack('<I', len(b)) + b

def _node(name, props=(), children=(), offset=0):
    pbytes = b''.join(_prop(p) for p in props)
    nm = name.encode('latin1')
    head = 13 + len(nm)
    body = b''
    pos = offset + head + len(pbytes)
    for c in children:
        cb = _node(c[0], c[1], c[2] if len(c) > 2 else (), pos)
        body += cb; pos += len(cb)
    if children:
        body += b'\0' * 13; pos += 13
    return struct.pack('<III', pos, len(props), len(pbytes)) + bytes([len(nm)]) + nm + pbytes + body

def _P(name, typ, label, flags, *vals): return ('P', (name, typ, label, flags) + vals)

def write_fbx(m, path, name, creator="Jamie's Market build_bangketa.py"):
    """Binary FBX 7.4, one mesh, per-corner normals and UVs: byte-for-byte the
    layout Jamie's Fortune's cabinet uses."""
    verts = [float(c) for v in m.v for c in v]
    index, normals, uvs = [], [], []
    for a, b, c in m.tri:
        index += [a, b, ~c]
        for k in (a, b, c):
            normals += [float(x) for x in m.n[k]]
    for (u, v) in m.t: uvs += [float(u), float(1.0 - v)]              # FBX has v = 0 at the bottom
    uvindex = [k for tri in m.tri for k in tri]
    GID, MID, MATID = _I64(700100), _I64(700200), _I64(700300)
    sep = '\x00\x01'
    tree = [
        ('FBXHeaderExtension', (), [('FBXHeaderVersion', (1003,)), ('FBXVersion', (7400,)), ('EncryptionType', (0,)),
                                    ('Creator', (creator,))]),
        ('GlobalSettings', (), [('Version', (1000,)), ('Properties70', (), [
            _P('UpAxis', 'int', 'Integer', '', 1), _P('UpAxisSign', 'int', 'Integer', '', 1),
            _P('FrontAxis', 'int', 'Integer', '', 2), _P('FrontAxisSign', 'int', 'Integer', '', 1),
            _P('CoordAxis', 'int', 'Integer', '', 0), _P('CoordAxisSign', 'int', 'Integer', '', 1),
            _P('OriginalUpAxis', 'int', 'Integer', '', -1), _P('OriginalUpAxisSign', 'int', 'Integer', '', 1),
            _P('UnitScaleFactor', 'double', 'Number', '', 100.0), _P('OriginalUnitScaleFactor', 'double', 'Number', '', 100.0)])]),
        ('Documents', (), [('Count', (1,)), ('Document', (_I64(700001), 'Scene', 'Scene'), [('RootNode', (_I64(0),))])]),
        ('References', ()),
        ('Definitions', (), [('Version', (100,)), ('Count', (4,)),
                             ('ObjectType', ('GlobalSettings',), [('Count', (1,))]),
                             ('ObjectType', ('Geometry',), [('Count', (1,))]),
                             ('ObjectType', ('Model',), [('Count', (1,))]),
                             ('ObjectType', ('Material',), [('Count', (1,))])]),
        ('Objects', (), [
            ('Geometry', (GID, name + sep + 'Geometry', 'Mesh'), [
                ('GeometryVersion', (124,)),
                ('Vertices', (_A('d', verts),)),
                ('PolygonVertexIndex', (_A('i', index),)),
                ('LayerElementNormal', (0,), [('Version', (101,)), ('Name', ('',)), ('MappingInformationType', ('ByPolygonVertex',)),
                                             ('ReferenceInformationType', ('Direct',)), ('Normals', (_A('d', normals),))]),
                ('LayerElementUV', (0,), [('Version', (101,)), ('Name', ('UVMap',)), ('MappingInformationType', ('ByPolygonVertex',)),
                                         ('ReferenceInformationType', ('IndexToDirect',)), ('UV', (_A('d', uvs),)), ('UVIndex', (_A('i', uvindex),))]),
                ('LayerElementMaterial', (0,), [('Version', (101,)), ('Name', ('',)), ('MappingInformationType', ('AllSame',)),
                                               ('ReferenceInformationType', ('IndexToDirect',)), ('Materials', (_A('i', [0]),))]),
                ('Layer', (0,), [('Version', (100,)),
                                 ('LayerElement', (), [('Type', ('LayerElementNormal',)), ('TypedIndex', (0,))]),
                                 ('LayerElement', (), [('Type', ('LayerElementUV',)), ('TypedIndex', (0,))]),
                                 ('LayerElement', (), [('Type', ('LayerElementMaterial',)), ('TypedIndex', (0,))])]),
            ]),
            ('Model', (MID, name + sep + 'Model', 'Mesh'), [
                ('Version', (232,)),
                ('Properties70', (), [_P('DefaultAttributeIndex', 'int', 'Integer', '', 0), _P('InheritType', 'enum', '', '', 1)]),
                ('MultiLayer', (0,)), ('MultiTake', (0,)), ('Shading', (_B(1),)), ('Culling', ('CullingOff',))]),
            ('Material', (MATID, name + sep + 'Material', ''), [
                ('Version', (102,)), ('ShadingModel', ('Phong',)), ('MultiLayer', (0,)),
                ('Properties70', (), [_P('DiffuseColor', 'Color', '', 'A', 0.8, 0.8, 0.8)])]),
        ]),
        ('Connections', (), [('C', ('OO', MID, _I64(0))), ('C', ('OO', GID, MID)), ('C', ('OO', MATID, MID))]),
        ('Takes', (), [('Current', ('',))]),
    ]
    out = b'Kaydara FBX Binary  \x00\x1a\x00' + struct.pack('<I', 7400)
    for n in tree:
        out += _node(n[0], n[1], n[2] if len(n) > 2 else (), len(out))
    out += b'\0' * 13
    out += bytes.fromhex('fabcab09d0c8d466b176fb831cf7267e') + b'\0' * 4
    pad = (16 - len(out) % 16) % 16
    out += b'\0' * (pad or 16)
    out += struct.pack('<I', 7400) + b'\0' * 120 + bytes.fromhex('f85a8c6adef5d97eece90ce3758f290b')
    open(path, 'wb').write(out)


# ============================================================================ software render (the game's iso camera)
FACING = {'E': (1, 0), 'S': (0, 1), 'W': (-1, 0), 'N': (0, -1)}
PX_XY, PX_Y2, PX_UP = 64.0, 32.0, 78.4          # per world unit, at the game's 2x tile scale

def render(m, colour, facing, canvas=(128, 256), anchor=(64, 224), ss=4, zoom=1, shadow=False, background=None):
    """Draws mesh m (textured with the RGBA/RGB image `colour`) standing on a tile, facing E/S/W/N."""
    canvas = (int(canvas[0] * zoom), int(canvas[1] * zoom)); anchor = (anchor[0] * zoom, anchor[1] * zoom)
    fx, fy = FACING[facing]; rx, ry = fy, -fx
    V = np.array(m.v); Nn = np.array(m.n); T = np.array(m.t)
    wx = V[:, 0] * rx + V[:, 2] * fx; wy = V[:, 0] * ry + V[:, 2] * fy; up = V[:, 1]
    nx = Nn[:, 0] * rx + Nn[:, 2] * fx; ny = Nn[:, 0] * ry + Nn[:, 2] * fy; nu = Nn[:, 1]
    sx = (anchor[0] + zoom * PX_XY * (wx - wy)) * ss; sy = (anchor[1] + zoom * (PX_Y2 * (wx + wy) - PX_UP * up)) * ss
    near = 0.612 * (wx + wy) + 0.5 * up
    W, H = canvas[0] * ss, canvas[1] * ss
    img = np.zeros((H, W, 4), dtype=np.float32); zbuf = np.full((H, W), -1e9, dtype=np.float32)
    C = np.asarray(colour.convert('RGB')).astype(np.float32) / 255.0
    L = np.array([0.35, 0.55, 0.75]); L = L / np.linalg.norm(L)            # (world x, world y, up): from the camera's left
    view = np.array([0.612, 0.612, 0.5])
    if shadow:
        # soft contact shadow: the footprint squashed onto the floor
        from PIL import ImageDraw, ImageFilter
        sh = Image.new('L', (W, H), 0); d = ImageDraw.Draw(sh)
        for a, b, c in m.tri:
            pts = [((anchor[0] + zoom * PX_XY * (wx[k] - wy[k])) * ss, (anchor[1] + zoom * PX_Y2 * (wx[k] + wy[k])) * ss) for k in (a, b, c)]
            d.polygon(pts, fill=110)
        sh = sh.filter(ImageFilter.GaussianBlur(3 * ss))
        img[..., 3] = np.asarray(sh).astype(np.float32) / 255.0 * 0.55
    for a, b, c in m.tri:
        fn = np.cross([sx[b] - sx[a], sy[b] - sy[a], 0], [sx[c] - sx[a], sy[c] - sy[a], 0])[2]
        if fn >= 0: continue                                                # back face (screen y is down)
        n = np.array([nx[a], ny[a], nu[a]])
        xs = np.array([sx[a], sx[b], sx[c]]); ys = np.array([sy[a], sy[b], sy[c]])
        x0, x1 = int(max(0, math.floor(xs.min()))), int(min(W - 1, math.ceil(xs.max())))
        y0, y1 = int(max(0, math.floor(ys.min()))), int(min(H - 1, math.ceil(ys.max())))
        if x1 < x0 or y1 < y0: continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        den = (ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2])
        if abs(den) < 1e-9: continue
        w0 = ((ys[1] - ys[2]) * (gx - xs[2]) + (xs[2] - xs[1]) * (gy - ys[2])) / den
        w1 = ((ys[2] - ys[0]) * (gx - xs[2]) + (xs[0] - xs[2]) * (gy - ys[2])) / den
        w2 = 1 - w0 - w1
        inside = (w0 >= -1e-4) & (w1 >= -1e-4) & (w2 >= -1e-4)
        z = w0 * near[a] + w1 * near[b] + w2 * near[c]
        sub = zbuf[y0:y1 + 1, x0:x1 + 1]
        win = inside & (z > sub)
        if not win.any(): continue
        u = np.clip(w0 * T[a, 0] + w1 * T[b, 0] + w2 * T[c, 0], 0, 1); v = np.clip(w0 * T[a, 1] + w1 * T[b, 1] + w2 * T[c, 1], 0, 1)
        tx = np.clip((u * C.shape[1]).astype(int), 0, C.shape[1] - 1); ty = np.clip((v * C.shape[0]).astype(int), 0, C.shape[0] - 1)
        col = C[ty, tx]
        # smooth-shaded faces interpolate their normals
        na = np.array([nx[a], ny[a], nu[a]]); nb = np.array([nx[b], ny[b], nu[b]]); nc = np.array([nx[c], ny[c], nu[c]])
        if np.allclose(na, nb) and np.allclose(na, nc):
            shade = min(1.0, 0.50 + 0.60 * max(0.0, float(n @ L)))
            col = col * shade
        else:
            nn = w0[..., None] * na + w1[..., None] * nb + w2[..., None] * nc
            nn = nn / np.maximum(1e-6, np.linalg.norm(nn, axis=-1, keepdims=True))
            shade = np.clip(0.50 + 0.60 * np.maximum(0.0, nn @ L), 0, 1.0)
            col = col * shade[..., None]
        tgt = img[y0:y1 + 1, x0:x1 + 1]
        tgt[win, :3] = col[win]; tgt[win, 3] = 1.0
        sub[win] = z[win]
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8), 'RGBA')
    im = im.resize(canvas, Image.LANCZOS)
    if background is not None:
        bg = Image.new('RGBA', canvas, background); bg.alpha_composite(im); im = bg
    return im


# ============================================================================ pack / tiles writers
def write_pack(path, page, sprites, max_width=2048, full=(128, 256)):
    """sprites: [(name, RGBA image of the full tile canvas)]; each is trimmed and
    shelf-packed on one page. Returns the sheet (for a look)."""
    trimmed = []
    for name, im in sprites:
        box = im.getbbox() or (0, 0, 1, 1)
        trimmed.append((name, im.crop(box), box))
    x = y = rowh = 0; pw = 0; places = []
    for name, im, box in trimmed:
        if x + im.width + 2 > max_width:
            x = 0; y += rowh + 2; rowh = 0
        places.append((x, y)); x += im.width + 2; rowh = max(rowh, im.height); pw = max(pw, x)
    ph = y + rowh
    sheet = Image.new('RGBA', (pw, ph), (0, 0, 0, 0))
    entries = []
    for (name, im, box), (px, py) in zip(trimmed, places):
        sheet.paste(im, (px, py))
        entries.append((name, px, py, im.width, im.height, box[0], box[1], full[0], full[1]))
    buf = io.BytesIO(); sheet.save(buf, 'PNG'); png = buf.getvalue()
    def s(t): b = t.encode('latin1'); return struct.pack('<i', len(b)) + b
    out = b'PZPK' + struct.pack('<i', 1) + struct.pack('<i', 1)
    out += s(page) + struct.pack('<i', len(entries)) + struct.pack('<i', 1)
    for e in entries: out += s(e[0]) + struct.pack('<8i', *e[1:])
    out += struct.pack('<i', len(png)) + png
    open(path, 'wb').write(out)
    return sheet

def read_pack(path):
    """Parses a pack written by write_pack (used to check the file)."""
    data = open(path, 'rb').read()
    assert data[:4] == b'PZPK'
    off = 4
    def i32():
        nonlocal off
        v = struct.unpack_from('<i', data, off)[0]; off += 4; return v
    def st():
        nonlocal off
        n = i32(); v = data[off:off + n].decode('latin1'); off += n; return v
    version, pages = i32(), i32()
    out = []
    for _ in range(pages):
        name = st(); count = i32(); alpha = i32()
        entries = []
        for _ in range(count):
            nm = st(); vals = [i32() for _ in range(8)]; entries.append((nm, vals))
        n = i32(); png = data[off:off + n]; off += n
        out.append((name, entries, Image.open(io.BytesIO(png))))
    assert off == len(data), 'trailing bytes in pack'
    return out

def write_tiles(path, tileset, tiles, cols=8):
    """Tile definition file: one tileset, `tiles` = list of property dicts (row-major)."""
    rows = max(1, (len(tiles) + cols - 1) // cols)
    def s(t): return t.encode('latin1') + b'\n'
    out = b'tdef' + struct.pack('<i', 1) + struct.pack('<i', 1)
    out += s(tileset) + s(tileset + '.png') + struct.pack('<4i', cols, rows, 1, cols * rows)
    for i in range(cols * rows):
        props = tiles[i] if i < len(tiles) else {}
        out += struct.pack('<i', len(props))
        for k, v in props.items(): out += s(k) + s(v)
    open(path, 'wb').write(out)

def read_tiles(path):
    data = open(path, 'rb').read()
    assert data[:4] == b'tdef'
    off = 4
    def i32():
        nonlocal off
        v = struct.unpack_from('<i', data, off)[0]; off += 4; return v
    def line():
        nonlocal off
        e = data.index(b'\n', off); v = data[off:e].decode('latin1'); off = e + 1; return v
    version, sets = i32(), i32()
    out = []
    for _ in range(sets):
        name, image = line(), line()
        cols, rows, number, count = i32(), i32(), i32(), i32()
        tiles = []
        for _ in range(count):
            n = i32(); props = {}
            for _ in range(n):
                k = line(); props[k] = line()
            tiles.append(props)
        out.append((name, image, cols, rows, number, tiles))
    assert off == len(data), 'trailing bytes in tiles'
    return out
