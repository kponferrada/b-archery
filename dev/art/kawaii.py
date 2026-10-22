"""Jamie's Treasures - the original mascot cast and how each one is built.

Everything is generated: no Blender, no third-party art. One character =
one 1024x1024 texture atlas (head, body, parts) shared by every 3D format
(figure, plush, capsule, monument), so a Mochi Mallow plush and a Mochi
Mallow figure always match. Flat formats (cards, acrylic stands, posters,
boxes) print a render of the same 3D model, so icons, cards and models agree.

Conventions (the same as Jamie's Market / Guilty Pleasures, known to load):
metres, Y up, front = +Z, standing on y = 0. Texture v = 0 is the TOP row.

STYLE GUIDE (docs/STYLE_GUIDE.md has the long version)
  * proportions  head : body about 1.35 : 1 in height, head wider than body,
                 stubby arms and feet, no neck
  * eyes         big vertical ovals set low on the face (just under the
                 head's equator), wide apart, two highlights (big top-left,
                 small bottom-right); sleepy and happy faces use soft arcs
  * cheeks       always a blush; its SHAPE is the character's signature
                 (star, heart, oval, sparkle, snowflake ...)
  * mouth        tiny, centred, between and below the eyes
  * colour       pastel base, one richer accent, dark eye colour is never
                 pure black (deep plum/navy/brown)
  * materials    figures: smooth with a faint top light; plush: soft fabric
                 grain and a seam line; gold only on Legendary details
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import core  # noqa: E402  (Jamie's Market's mesh / FBX / pack / tile writers)
import meadow as MW  # noqa: E402  (the 16 Meadow friends, 0.3.0)

FONT_BOLD = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
TAU = 2 * math.pi


def font(size):
    try:
        return ImageFont.truetype(FONT_BOLD, size)
    except OSError:
        return ImageFont.load_default()


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


# =========================================================================== the cast
# Every character: colours, face, signature blush, silhouette parts.
#   eyes   "round" | "sleepy" | "happy" | "smug" | "sparkle"
#   mouth  "w" (cat mouth) | "smile" | "open" | "smirk" | "o"
#   blush  "star" | "heart" | "oval" | "sparkle" | "flake" | "flame" | "leaf" | "dot"
#   parts  list of builders applied on top of the shared chibi base
CAST = {
    "MochiMallow": dict(
        name="Mochi Mallow", personality="sleepy and soft, naps on anything warm",
        body=(250, 246, 255), belly=(236, 228, 252), accent=(196, 178, 245), accent2=(255, 214, 120),
        eye=(74, 58, 104), blush_c=(255, 164, 196), eyes="sleepy", mouth="w", blush="star",
        head=(0.40, 0.32, 0.34), parts=["cloud_puffs", "star_tummy"], pose="sit",
    ),
    "Kurobun": dict(
        name="Kurobun", personality="midnight trickster, hides snacks in its ears",
        body=(64, 70, 128), belly=(210, 218, 252), accent=(250, 212, 112), accent2=(150, 160, 230),
        eye=(46, 42, 92), blush_c=(170, 150, 235), eyes="smug", mouth="smirk", blush="oval",
        head=(0.36, 0.31, 0.32), parts=["floppy_ears", "crescent_charm", "face_mask"], pose="stand",
    ),
    "Berrybell": dict(
        name="Berrybell", personality="cheerful forest sprite, rings a tiny bell when happy",
        body=(244, 104, 124), belly=(255, 226, 226), accent=(126, 204, 112), accent2=(255, 236, 150),
        eye=(96, 40, 56), blush_c=(255, 170, 160), eyes="round", mouth="open", blush="heart",
        head=(0.37, 0.32, 0.33), parts=["leaf_ears", "berry_seeds", "calyx", "face_mask"], pose="stand",
    ),
    "LumiPuff": dict(
        name="Lumi Puff", personality="dreamy moon moth that glows a little at night",
        body=(255, 248, 232), belly=(255, 255, 248), accent=(186, 226, 214), accent2=(214, 196, 246),
        eye=(60, 70, 110), blush_c=(255, 190, 210), eyes="sparkle", mouth="o", blush="sparkle",
        head=(0.35, 0.31, 0.32), parts=["moth_wings", "antennae", "fluff_collar"], pose="stand",
    ),
    "BobaBear": dict(
        name="Boba Bear", personality="tea-shop regular, always shares the last pearl",
        body=(206, 164, 124), belly=(248, 232, 206), accent=(246, 156, 176), accent2=(92, 62, 50),
        eye=(70, 44, 36), blush_c=(250, 150, 140), eyes="happy", mouth="open", blush="oval",
        head=(0.38, 0.32, 0.33), parts=["bear_ears", "muzzle", "boba_scarf"], pose="sit",
    ),
    "Pipkin": dict(
        name="Pipkin", personality="tiny pumpkin spirit, cozy, loves blankets",
        body=(250, 156, 70), belly=(255, 214, 160), accent=(112, 186, 92), accent2=(150, 96, 52),
        eye=(92, 52, 36), blush_c=(255, 120, 100), eyes="happy", mouth="smile", blush="leaf",
        head=(0.38, 0.30, 0.34), parts=["pumpkin_ribs", "sprout"], pose="stand",
    ),
    "NebulaNeko": dict(
        name="Nebula Neko", personality="curious cosmic cat, counts the stars every night",
        body=(92, 82, 168), belly=(186, 182, 240), accent=(255, 226, 140), accent2=(250, 156, 206),
        eye=(255, 220, 120), blush_c=(250, 156, 206), eyes="round", mouth="w", blush="dot",
        head=(0.37, 0.31, 0.32), parts=["cat_ears", "constellations", "star_tail", "face_mask"], pose="stand",
    ),
    "Frostbit": dict(
        name="Frostbit", personality="marshmallow snow critter, gets shy when warm",
        body=(242, 250, 255), belly=(222, 240, 252), accent=(150, 210, 245), accent2=(200, 236, 255),
        eye=(60, 92, 132), blush_c=(170, 210, 250), eyes="round", mouth="o", blush="flake",
        head=(0.38, 0.33, 0.34), parts=["crystal_ears", "frost_tummy"], pose="sit",
    ),
    "EmberCub": dict(
        name="Ember Cub", personality="little fire guardian, warm hugs only",
        body=(246, 120, 84), belly=(255, 214, 150), accent=(255, 196, 70), accent2=(255, 242, 170),
        eye=(90, 36, 30), blush_c=(255, 236, 140), eyes="happy", mouth="open", blush="flame",
        head=(0.37, 0.31, 0.33), parts=["bear_ears_small", "flame_tuft", "glow_tummy"], pose="stand",
    ),
    "Mossling": dict(
        name="Mossling", personality="round woodland napper, mushrooms grow on its head",
        body=(146, 196, 122), belly=(206, 232, 178), accent=(236, 108, 108), accent2=(255, 248, 236),
        eye=(56, 76, 46), blush_c=(250, 170, 150), eyes="sleepy", mouth="smile", blush="oval",
        head=(0.40, 0.33, 0.35), parts=["moss_tufts", "mushrooms"], pose="sit",
    ),
}
ORDER = ["MochiMallow", "Kurobun", "Berrybell", "LumiPuff", "BobaBear", "Pipkin", "NebulaNeko", "Frostbit", "EmberCub", "Mossling"]
CAST.update(MW.CAST)
ORDER = ORDER + MW.ORDER


# =========================================================================== painting
SS = 4  # supersampling for painted regions


class Painter:
    """Paints on an equirectangular region (longitude across, latitude down).
    lon 0 = the front (+Z), lat 0 = the equator. Works at SS x size, then shrinks."""

    def __init__(self, w, h, base):
        self.w, self.h = w * SS, h * SS
        self.img = Image.new("RGBA", (self.w, self.h), base + (255,))
        self.d = ImageDraw.Draw(self.img)

    def xy(self, lon, lat):
        return ((lon / TAU + 0.5) * self.w, (0.5 - lat / math.pi) * self.h)

    def k(self):  # pixels per radian (same both ways)
        return self.w / TAU

    def ellipse(self, lon, lat, rx, ry, fill, outline=None, width=0):
        x, y = self.xy(lon, lat)
        k = self.k()
        self.d.ellipse([x - rx * k, y - ry * k, x + rx * k, y + ry * k], fill=fill, outline=outline, width=int(width * k))

    def arc(self, lon, lat, rx, ry, start, end, fill, width):
        x, y = self.xy(lon, lat)
        k = self.k()
        self.d.arc([x - rx * k, y - ry * k, x + rx * k, y + ry * k], start, end, fill=fill, width=max(1, int(width * k)))

    def poly(self, pts, fill):
        self.d.polygon([self.xy(a, b) for a, b in pts], fill=fill)

    def line(self, pts, fill, width):
        self.d.line([self.xy(a, b) for a, b in pts], fill=fill, width=max(1, int(width * self.k())), joint="curve")

    def star(self, lon, lat, r, fill, points=5, inner=0.45, rot=-90):
        pts = []
        for i in range(points * 2):
            rr = r if i % 2 == 0 else r * inner
            a = math.radians(rot + i * 180 / points)
            pts.append((lon + rr * math.cos(a), lat - rr * math.sin(a)))
        self.poly(pts, fill)

    def heart(self, lon, lat, r, fill):
        pts = []
        for i in range(60):
            t = TAU * i / 60
            x = 16 * math.sin(t) ** 3
            y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
            pts.append((lon + x / 17 * r, lat + y / 17 * r))
        self.poly(pts, fill)

    def done(self, w, h, grain=0.0, seed=1):
        img = self.img.resize((w, h), Image.LANCZOS)
        if grain > 0:
            rng = np.random.default_rng(seed)
            a = np.asarray(img).astype(np.float32)
            n = rng.normal(0, 1, (h, w, 1)).astype(np.float32)
            n = np.asarray(Image.fromarray(((n[..., 0] * 40 + 128).clip(0, 255)).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))).astype(np.float32)[..., None] - 128
            a[..., :3] = np.clip(a[..., :3] * (1 + grain * n / 128.0), 0, 255)
            img = Image.fromarray(a.astype(np.uint8), "RGBA")
        return img


def paint_face(p, c, lat0=-0.10):
    """Eyes, blush and mouth, centred on the front of the head."""
    eye = c["eye"] + (255,)
    ex, ey = 0.37, lat0
    style = c["eyes"]
    for side in (-1, 1):
        x = side * ex
        if style in ("round", "sparkle", "smug"):
            p.ellipse(x, ey, 0.135, 0.185, eye)
            if style == "smug":  # half-lidded: body colour lid over the top
                p.ellipse(x, ey + 0.15, 0.17, 0.10, c["belly"] + (255,))
                p.arc(x, ey + 0.06, 0.14, 0.05, 180, 360, shade(c["eye"], 1.0) + (255,), 0.03)
            hl = (255, 255, 255, 255)
            p.ellipse(x - 0.045, ey + 0.065, 0.052, 0.06, hl)
            p.ellipse(x + 0.05, ey - 0.08, 0.026, 0.026, hl)
            if style == "sparkle":
                p.star(x + 0.035, ey + 0.035, 0.03, hl, points=4, inner=0.35)
        elif style == "sleepy":
            p.arc(x, ey + 0.03, 0.12, 0.08, 20, 160, eye, 0.042)
            p.line([(x + side * 0.09, ey + 0.05), (x + side * 0.13, ey + 0.085)], eye, 0.018)
        elif style == "happy":
            p.arc(x, ey - 0.04, 0.125, 0.11, 200, 340, eye, 0.046)
    # blush (the signature)
    bl = c["blush_c"] + (230,)
    bx, by = 0.60, ey - 0.15
    for side in (-1, 1):
        x = side * bx
        b = c["blush"]
        if b == "star":
            p.star(x, by, 0.095, bl)
        elif b == "heart":
            p.heart(x, by, 0.085, bl)
        elif b == "sparkle":
            p.star(x, by, 0.075, bl, points=4, inner=0.3)
            p.star(x + side * 0.08, by + 0.07, 0.03, bl, points=4, inner=0.3)
        elif b == "flake":
            for k in range(3):
                a = math.radians(30 + 60 * k)
                p.line([(x - 0.07 * math.cos(a), by - 0.07 * math.sin(a)), (x + 0.07 * math.cos(a), by + 0.07 * math.sin(a))], bl, 0.016)
        elif b == "flame":
            p.poly([(x, by + 0.08), (x + 0.05, by - 0.01), (x + 0.03, by - 0.05), (x, by - 0.06), (x - 0.03, by - 0.05), (x - 0.05, by - 0.01)], bl)
        elif b == "leaf":
            p.poly([(x - 0.07, by), (x, by + 0.045), (x + 0.07, by), (x, by - 0.045)], bl)
        elif b == "dot":
            for k in range(3):
                p.ellipse(x + (k - 1) * 0.045, by, 0.016, 0.016, bl)
        elif MW.blush(p, b, x, by, side, bl):
            pass
        else:
            p.ellipse(x, by, 0.12, 0.07, bl)
    # mouth
    m = c["mouth"]
    mc = shade(c["eye"], 0.9) + (255,)
    my = ey - 0.20
    if m == "w":
        p.arc(-0.035, my, 0.035, 0.03, 0, 180, mc, 0.016)
        p.arc(0.035, my, 0.035, 0.03, 0, 180, mc, 0.016)
    elif m == "smile":
        p.arc(0, my + 0.02, 0.06, 0.05, 20, 160, mc, 0.018)
    elif m == "open":
        p.d.chord([*p.xy(-0.055, my + 0.03), *p.xy(0.055, my - 0.07)], 0, 180, fill=mc)
        p.ellipse(0, my - 0.045, 0.028, 0.016, (246, 120, 130, 255))
    elif m == "smirk":
        p.arc(0.02, my + 0.02, 0.06, 0.04, 10, 120, mc, 0.017)
        p.ellipse(-0.035, my + 0.005, 0.008, 0.008, mc)
    elif m == "o":
        p.ellipse(0, my, 0.022, 0.026, mc)
    # "none": a beak instead (a 3D part)


def paint_head(c, w=512, h=256, grain=0.0):
    p = Painter(w, h, c["body"])
    parts = c["parts"]
    if "face_mask" in parts:  # a lighter face patch (bunny / cat / berry faces)
        p.ellipse(0, -0.12, 0.95, 0.62, c["belly"] + (255,))
    if "muzzle" in parts:
        p.ellipse(0, -0.24, 0.30, 0.17, c["belly"] + (255,))
        p.ellipse(0, -0.17, 0.07, 0.05, shade(c["accent2"], 1.0) + (255,))
    if "berry_seeds" in parts:
        rng = np.random.default_rng(3)
        for _ in range(70):
            lon = rng.uniform(-math.pi, math.pi)
            lat = rng.uniform(-1.2, 1.1)
            if abs(lon) < 1.2 and lat < 0.35 and lat > -0.75:
                continue  # keep the face clear
            p.ellipse(lon, lat, 0.035, 0.05, c["accent2"] + (255,))
    if "constellations" in parts:
        rng = np.random.default_rng(7)
        pts = [(rng.uniform(1.4, 4.9), rng.uniform(-0.6, 1.2)) for _ in range(9)]
        pts = [((a + math.pi) % TAU - math.pi, b) for a, b in pts]
        for i in range(len(pts) - 1):
            if abs(pts[i][0] - pts[i + 1][0]) < 1.5:
                p.line([pts[i], pts[i + 1]], c["accent"] + (150,), 0.012)
        for a, b in pts:
            p.star(a, b, 0.05, c["accent"] + (255,), points=4, inner=0.35)
        p.star(0.0, 0.62, 0.09, c["accent"] + (255,), points=4, inner=0.35)  # forehead star
    if "pumpkin_ribs" in parts:
        for k in range(8):
            lon = -math.pi + k * TAU / 8 + TAU / 16
            p.line([(lon, 1.4), (lon, -1.4)], shade(c["body"], 0.86) + (255,), 0.05)
    if "frost_tummy" in parts:
        pass
    MW.paint_head_extra(p, c)
    paint_face(p, c)
    return p.done(w, h, grain=grain)


def paint_body(c, w=256, h=128, grain=0.0):
    p = Painter(w, h, c["body"])
    p.ellipse(0, -0.1, 0.85, 0.75, c["belly"] + (255,))  # tummy patch
    parts = c["parts"]
    if "star_tummy" in parts:
        p.star(0, 0.0, 0.22, c["accent"] + (255,))
    if "glow_tummy" in parts:
        p.ellipse(0, 0.0, 0.32, 0.28, c["accent2"] + (255,))
    if "frost_tummy" in parts:
        for k in range(3):
            a = math.radians(90 + 60 * k)
            p.line([(-0.22 * math.cos(a), -0.22 * math.sin(a)), (0.22 * math.cos(a), 0.22 * math.sin(a))], c["accent"] + (255,), 0.05)
    if "constellations" in parts:
        rng = np.random.default_rng(11)
        for _ in range(8):
            p.star(rng.uniform(1.4, 4.9) - math.pi, rng.uniform(-0.6, 0.8), 0.06, c["accent"] + (255,), points=4, inner=0.35)
    if "berry_seeds" in parts:
        rng = np.random.default_rng(5)
        for _ in range(40):
            lon = rng.uniform(-math.pi, math.pi)
            if abs(lon) < 1.0:
                continue
            p.ellipse(lon, rng.uniform(-1.0, 1.0), 0.04, 0.06, c["accent2"] + (255,))
    if "pumpkin_ribs" in parts:
        for k in range(8):
            lon = -math.pi + k * TAU / 8
            p.line([(lon, 1.4), (lon, -1.4)], shade(c["body"], 0.86) + (255,), 0.06)
    MW.paint_body_extra(p, c)
    return p.done(w, h, grain=grain)


def swatch(colour, size=64, grad=True, grain=0.0, pattern=None, c=None):
    im = Image.new("RGBA", (size, size), colour + (255,))
    if grad:
        d = ImageDraw.Draw(im)
        for y in range(size):
            k = 1.08 - 0.16 * y / size
            d.line([(0, y), (size, y)], fill=shade(colour, k) + (255,))
    if pattern == "boba":
        d = ImageDraw.Draw(im)
        for i in range(4):
            for j in range(4):
                x, y = 8 + i * 16 + (j % 2) * 8, 8 + j * 16
                d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=c["accent2"] + (255,))
    if pattern == "crescent":
        d = ImageDraw.Draw(im)
        d.ellipse([10, 10, 54, 54], fill=colour + (255,))
        d.ellipse([22, 6, 62, 46], fill=shade(colour, 0.7) + (255,))
    if pattern == "wing":
        d = ImageDraw.Draw(im)
        d.ellipse([18, 18, 46, 46], fill=c["accent2"] + (255,))
        d.ellipse([26, 26, 38, 38], fill=(255, 255, 255, 255))
    if pattern == "mushroom":
        d = ImageDraw.Draw(im)
        for (x, y, r) in [(16, 20, 6), (44, 14, 5), (36, 42, 7), (10, 48, 4), (54, 50, 4)]:
            d.ellipse([x - r, y - r, x + r, y + r], fill=c["accent2"] + (255,))
    if grain > 0:
        rng = np.random.default_rng(size)
        a = np.asarray(im).astype(np.float32)
        a[..., :3] = np.clip(a[..., :3] * (1 + grain * rng.normal(0, 0.5, (size, size, 1))), 0, 255)
        im = Image.fromarray(a.astype(np.uint8), "RGBA")
    return im


# =========================================================================== meshes
class Builder:
    """Smooth surfaces straight into a core.Mesh with atlas UVs."""

    def __init__(self, atlas):
        self.A = atlas
        self.m = core.Mesh()

    def _emit(self, P, N, UV):
        """P, N, UV: grids [rows][cols] (rows from bottom to top). Wound per normals."""
        m = self.m
        rows, cols = len(P), len(P[0])
        for i in range(rows - 1):
            for j in range(cols - 1):
                quad = [(i, j), (i, j + 1), (i + 1, j + 1), (i + 1, j)]
                for tri in ((0, 1, 2), (0, 2, 3)):
                    ids = [quad[t] for t in tri]
                    pts = [np.array(P[a][b]) for a, b in ids]
                    g = np.cross(pts[1] - pts[0], pts[2] - pts[0])
                    if np.linalg.norm(g) < 1e-11:
                        continue
                    nrm = sum(np.array(N[a][b]) for a, b in ids)
                    if g @ nrm < 0:
                        ids = [ids[0], ids[2], ids[1]]
                    b = len(m.v)
                    for a_, b_ in ids:
                        m.v.append(np.array(P[a_][b_], dtype=float))
                        nn = np.array(N[a_][b_], dtype=float)
                        # keep normals consistent with the face (check() wants > 0.05)
                        gn = g / np.linalg.norm(g)
                        if gn @ nn < 0:
                            nn = gn
                        if gn @ nn < 0.2:
                            nn = (nn + gn)
                        m.n.append(nn / np.linalg.norm(nn))
                        m.t.append(UV[a_][b_])
                    m.tri.append((b, b + 1, b + 2))

    def surface(self, fn, region, nu=24, nv=14, xform=None, sub=(0, 0, 1, 1)):
        """fn(lon, lat) -> local point. lon -pi..pi (0 = front), lat -pi/2..pi/2."""
        R = np.eye(3) if xform is None else xform[0]
        T = np.zeros(3) if xform is None else np.array(xform[1])
        P, UV = [], []
        for i in range(nv + 1):
            lat = -math.pi / 2 + math.pi * i / nv
            row, urow = [], []
            for j in range(nu + 1):
                lon = -math.pi + TAU * j / nu
                row.append(R @ np.array(fn(lon, lat)) + T)
                u = sub[0] + (sub[2] - sub[0]) * (j / nu)
                v = sub[1] + (sub[3] - sub[1]) * (0.5 - lat / math.pi)
                urow.append(self.A.point(region, min(max(u, 0.002), 0.998), min(max(v, 0.002), 0.998)))
            P.append(row)
            UV.append(urow)
        N = []
        for i in range(nv + 1):
            nrow = []
            for j in range(nu + 1):
                a = P[i][min(j + 1, nu)] - P[i][max(j - 1, 0)]
                if j == 0 or j == nu:
                    a = P[i][1] - P[i][nu - 1]
                b = P[min(i + 1, nv)][j] - P[max(i - 1, 0)][j]
                n = np.cross(a, b)
                if np.linalg.norm(n) < 1e-10:  # pole
                    centre = np.mean([P[i][k] for k in range(nu)], axis=0)
                    other = np.mean([P[1 if i == 0 else nv - 1][k] for k in range(nu)], axis=0)
                    n = centre - other
                nrow.append(n / (np.linalg.norm(n) or 1))
            N.append(nrow)
        # make normals point outward: compare with direction from the shape's centre
        centre = np.mean([p for row in P for p in row], axis=0)
        flip = sum(((P[i][j] - centre) @ N[i][j]) for i in range(nv + 1) for j in range(nu + 1)) < 0
        if flip:
            N = [[-n for n in row] for row in N]
        self._emit(P, N, UV)

    def ellipsoid(self, centre, radii, region, rot=None, nu=24, nv=14, sub=(0, 0, 1, 1), bulge=None):
        rx, ry, rz = radii

        def fn(lon, lat):
            k = 1.0 if bulge is None else bulge(lon, lat)
            return (rx * k * math.cos(lat) * math.sin(lon), ry * math.sin(lat), rz * k * math.cos(lat) * math.cos(lon))
        self.surface(fn, region, nu, nv, (rot if rot is not None else np.eye(3), centre), sub)

    def lathe(self, profile, region, base=(0, 0, 0), rot=None, nu=20, sub=(0, 0, 1, 1), squash=(1, 1), scale=1.0):
        """profile: [(radius, height)] bottom to top; radius 0 at the ends closes the shape."""
        profile = [(r * scale, h * scale) for r, h in profile]
        nv = len(profile) - 1

        def fn(lon, lat):
            t = (lat + math.pi / 2) / math.pi * nv
            i = min(int(t), nv - 1)
            f = t - i
            r = profile[i][0] + (profile[i + 1][0] - profile[i][0]) * f
            y = profile[i][1] + (profile[i + 1][1] - profile[i][1]) * f
            return (r * squash[0] * math.sin(lon), y, r * squash[1] * math.cos(lon))
        self.surface(fn, region, nu, nv * 2, (rot if rot is not None else np.eye(3), base), sub)

    def disc_base(self, r, h, region_top, region_side, y0=0.0, n=32):
        """A round display base (cylinder with a top)."""
        m = self.m
        for j in range(n):
            a0, a1 = TAU * j / n, TAU * (j + 1) / n
            p = [(r * math.sin(a0), y0, r * math.cos(a0)), (r * math.sin(a1), y0, r * math.cos(a1)),
                 (r * math.sin(a1), y0 + h, r * math.cos(a1)), (r * math.sin(a0), y0 + h, r * math.cos(a0))]
            nrm = [(math.sin(a0), 0, math.cos(a0)), (math.sin(a1), 0, math.cos(a1)), (math.sin(a1), 0, math.cos(a1)), (math.sin(a0), 0, math.cos(a0))]
            uv = [self.A.point(region_side, j / n, 0.95), self.A.point(region_side, (j + 1) / n, 0.95),
                  self.A.point(region_side, (j + 1) / n, 0.05), self.A.point(region_side, j / n, 0.05)]
            m.quad(p, uv, normals=nrm)
            c = (0, y0 + h, 0)
            tp = [c, p[3], p[2]]
            tuv = [self.A.point(region_top, 0.5, 0.5),
                   self.A.point(region_top, 0.5 + 0.48 * math.sin(a0), 0.5 - 0.48 * math.cos(a0)),
                   self.A.point(region_top, 0.5 + 0.48 * math.sin(a1), 0.5 - 0.48 * math.cos(a1))]
            m.triangle(tp, tuv)


def rot_xyz(rx=0, ry=0, rz=0):
    def R(axis, d):
        return core._rot(axis, d)
    return R("y", ry) @ R("x", rx) @ R("z", rz)


# =========================================================================== one character
def character_atlas(key, plush=False, legendary=False, size=1024, extra=None):
    """The texture every 3D format of this character shares."""
    c = CAST[key]
    g = 0.10 if plush else 0.0
    A = core.Atlas(size, background=c["body"] + (255,))
    A.add("head", paint_head(c, 512, 256, grain=g))
    A.add("body", paint_body(c, 256, 128, grain=g))
    A.add("main", swatch(c["body"], grain=g))
    A.add("dark", swatch(shade(c["body"], 0.88), grain=g))
    A.add("belly", swatch(c["belly"], grain=g))
    A.add("accent", swatch(c["accent"], grain=g))
    A.add("accent2", swatch(c["accent2"], grain=g))
    A.add("gold", swatch((246, 196, 72)))
    A.add("goldsoft", swatch((255, 226, 140)))
    A.add("scarf", swatch(c["accent"], pattern="boba", c=c, grain=g))
    A.add("crescent", swatch(c["accent"], pattern="crescent"))
    A.add("wing", swatch(c["accent"], pattern="wing", c=c, grain=g))
    A.add("wing2", swatch(c["accent2"], pattern="wing", c={"accent2": c["accent"]}, grain=g))
    A.add("cap", swatch(c["accent"], pattern="mushroom", c=c))
    A.add("cream", swatch((250, 244, 236)))
    A.add("capsule", swatch(mix(c["accent"], (255, 255, 255), 0.35)))
    # display bases
    A.add("base_top", base_top_art(c, legendary))
    A.add("base_side", swatch((250, 238, 246) if not legendary else (246, 206, 96)))
    A.add("pedestal", swatch((236, 226, 240)))
    A.add("pedestal_top", base_top_art(c, True, size=256))
    for name, img in PROP_SWATCHES().items():
        A.add(name, img)
    for name, img in MW.swatches(c, swatch, grain=g).items():
        A.add(name, img)
    for name, img in (extra or {}).items():
        A.add(name, img)
    return A.finish()


def base_top_art(c, legendary, size=128):
    im = Image.new("RGBA", (size * SS, size * SS), (255, 244, 250, 255) if not legendary else (255, 232, 160, 255))
    d = ImageDraw.Draw(im)
    S = size * SS
    ring = c["accent"] if not legendary else (226, 170, 50)
    d.ellipse([S * 0.04, S * 0.04, S * 0.96, S * 0.96], outline=ring + (255,), width=int(S * 0.05))
    for k in range(5):  # little stars around the rim
        a = TAU * k / 5 - math.pi / 2
        x, y = S / 2 + S * 0.36 * math.cos(a), S / 2 + S * 0.36 * math.sin(a)
        r = S * 0.05
        pts = []
        for i in range(10):
            rr = r if i % 2 == 0 else r * 0.45
            aa = -math.pi / 2 + i * math.pi / 5
            pts.append((x + rr * math.cos(aa), y + rr * math.sin(aa)))
        d.polygon(pts, fill=ring + (255,))
    return im.resize((size, size), Image.LANCZOS)


def build_character(B, key, height=1.0, pose=None, plush=False, props=True, bag=False):
    """The shared chibi body. Returns nothing; adds to B.m. Units: height ~ 1 before scaling.
    props=False leaves off a held object (Fiesta figures hold their own prop).
    bag=True leaves off what sticks out of the back (tails, a backpack): the worn
    mascot bags rest their back against the wearer."""
    c = CAST[key]
    s = height
    pose = pose or c["pose"]
    hx, hy, hz = c["head"]
    sit = pose == "sit"
    by = 0.24 if not sit else 0.20
    head_y = 0.66 if not sit else 0.60
    soft = 1.06 if plush else 1.0
    # body
    B.ellipsoid((0, by * s, 0), (0.25 * s * soft, 0.24 * s, 0.22 * s * soft), "body", nu=24, nv=12)
    # head (pumpkins get ribs)
    bulge = None
    if "pumpkin_ribs" in c["parts"]:
        bulge = lambda lon, lat: 1.0 + 0.045 * math.cos(8 * lon)  # noqa: E731
    B.ellipsoid((0, head_y * s, 0.01 * s), (hx * s, hy * s, hz * s), "head", nu=40, nv=22, bulge=bulge)
    # arms (the birds have wings instead, from their parts)
    if c.get("arms", True):
        for side in (-1, 1):
            B.ellipsoid((side * 0.25 * s, (by + 0.04) * s, 0.04 * s), (0.075 * s, 0.11 * s, 0.075 * s), "main",
                        rot=rot_xyz(rz=side * 35, rx=-15), nu=12, nv=8)
    # feet
    for side in (-1, 1):
        if sit:
            B.ellipsoid((side * 0.12 * s, 0.07 * s, 0.17 * s), (0.085 * s, 0.07 * s, 0.11 * s), c.get("feet", "belly"), nu=12, nv=8)
        else:
            B.ellipsoid((side * 0.11 * s, 0.045 * s, 0.05 * s), (0.09 * s, 0.05 * s, 0.11 * s), c.get("feet", "dark"), nu=12, nv=8)
    top = head_y + hy
    P = c["parts"]
    if "cloud_puffs" in P:
        for (x, y, z, r) in [(-0.24, 0.20, 0.0, 0.15), (0.24, 0.20, 0.0, 0.15), (-0.10, 0.27, -0.02, 0.15),
                             (0.10, 0.27, -0.02, 0.15), (0.0, 0.22, -0.18, 0.15), (-0.34, 0.03, -0.02, 0.12), (0.34, 0.03, -0.02, 0.12)]:
            B.ellipsoid((x * s, (head_y + y) * s, z * s), (r * s, r * 0.9 * s, r * s), "main", nu=16, nv=10)
        B.ellipsoid((0, (by - 0.04) * s, -0.22 * s), (0.09 * s, 0.08 * s, 0.07 * s), "main", nu=12, nv=8)  # puff tail
    if "floppy_ears" in P:
        for side in (-1, 1):
            B.ellipsoid((side * 0.33 * s, (head_y + 0.02) * s, -0.02 * s), (0.08 * s, 0.30 * s, 0.07 * s), "main",
                        rot=rot_xyz(rz=side * 18, rx=8), nu=16, nv=12)
            B.ellipsoid((side * 0.345 * s, (head_y + 0.0) * s, 0.04 * s), (0.05 * s, 0.24 * s, 0.03 * s), "accent2",
                        rot=rot_xyz(rz=side * 18, rx=8), nu=12, nv=8)
        B.ellipsoid((0, (by - 0.06) * s, -0.23 * s), (0.08 * s, 0.08 * s, 0.07 * s), "belly", nu=12, nv=8)
    if "crescent_charm" in P:
        B.ellipsoid((0.27 * s, (top - 0.06) * s, 0.10 * s), (0.065 * s, 0.065 * s, 0.022 * s), "crescent",
                    rot=rot_xyz(rz=-20), nu=16, nv=8)
    if "leaf_ears" in P:
        for side in (-1, 1):
            B.ellipsoid((side * 0.30 * s, (top - 0.02) * s, 0.0), (0.07 * s, 0.17 * s, 0.03 * s), "accent",
                        rot=rot_xyz(rz=-side * 38, ry=side * 15), nu=14, nv=10)
    if "calyx" in P:
        for k in range(5):
            a = TAU * k / 5
            B.ellipsoid((0.08 * math.sin(a) * s, (top - 0.015) * s, 0.08 * math.cos(a) * s), (0.03 * s, 0.015 * s, 0.09 * s),
                        "accent", rot=rot_xyz(ry=math.degrees(a)), nu=10, nv=6)
        B.lathe([(0.0, 0), (0.018, 0.02), (0.012, 0.09), (0.0, 0.10)], "accent", base=(0, (top - 0.02) * s, 0), nu=10, scale=s)
    if "moth_wings" in P:
        for side in (-1, 1):
            B.ellipsoid((side * 0.30 * s, (by + 0.22) * s, -0.20 * s), (0.30 * s, 0.24 * s, 0.025 * s), "wing",
                        rot=rot_xyz(rz=side * 22, ry=-side * 25), nu=20, nv=10)
            B.ellipsoid((side * 0.24 * s, (by - 0.02) * s, -0.18 * s), (0.18 * s, 0.14 * s, 0.022 * s), "wing2",
                        rot=rot_xyz(rz=-side * 25, ry=-side * 25), nu=16, nv=8)
    if "antennae" in P:
        for side in (-1, 1):
            B.lathe([(0.0, 0), (0.012, 0.0), (0.010, 0.18), (0.0, 0.19)], "accent2", base=(side * 0.12 * s, (top - 0.05) * s, 0),
                    rot=rot_xyz(rz=-side * 28), nu=8, scale=s)
            B.ellipsoid((side * 0.215 * s, (top + 0.115) * s, 0), (0.05 * s, 0.05 * s, 0.05 * s), "accent", nu=12, nv=8)
    if "fluff_collar" in P:
        for k in range(10):
            a = TAU * k / 10
            B.ellipsoid((0.22 * math.sin(a) * s, (by + 0.19) * s, 0.20 * math.cos(a) * s), (0.08 * s, 0.065 * s, 0.08 * s), "cream", nu=10, nv=6)
    if "bear_ears" in P or "bear_ears_small" in P:
        r = 0.11 if "bear_ears" in P else 0.085
        for side in (-1, 1):
            B.ellipsoid((side * 0.25 * s, (top - 0.06) * s, -0.02 * s), (r * s, r * s, r * 0.7 * s), "main", nu=14, nv=10)
            B.ellipsoid((side * 0.25 * s, (top - 0.06) * s, (r * 0.45) * s), (r * 0.6 * s, r * 0.6 * s, r * 0.25 * s), "belly", nu=12, nv=8)
        B.ellipsoid((0, (by - 0.08) * s, -0.21 * s), (0.06 * s, 0.06 * s, 0.05 * s), "main", nu=10, nv=6)
    if "boba_scarf" in P:
        B.lathe([(0.0, -0.02), (0.25, -0.02), (0.27, 0.03), (0.25, 0.08), (0.0, 0.08)], "scarf", base=(0, (by + 0.15) * s, 0), nu=28, scale=s)
        B.ellipsoid((0.14 * s, (by + 0.05) * s, 0.21 * s), (0.06 * s, 0.11 * s, 0.025 * s), "scarf", rot=rot_xyz(rz=12), nu=10, nv=8)
    if "sprout" in P:
        B.lathe([(0.0, 0), (0.03, 0.0), (0.025, 0.08), (0.0, 0.09)], "accent2", base=(0, (top - 0.03) * s, 0), nu=10, scale=s)
        B.ellipsoid((0.08 * s, (top + 0.08) * s, 0), (0.09 * s, 0.025 * s, 0.05 * s), "accent", rot=rot_xyz(rz=25), nu=14, nv=8)
        B.ellipsoid((-0.05 * s, (top + 0.07) * s, 0.02 * s), (0.06 * s, 0.02 * s, 0.035 * s), "accent", rot=rot_xyz(rz=-30), nu=12, nv=6)
    if "cat_ears" in P:
        for side in (-1, 1):
            B.lathe([(0.0, 0), (0.11, 0.0), (0.06, 0.10), (0.0, 0.17)], "main", base=(side * 0.21 * s, (top - 0.10) * s, -0.02 * s),
                    rot=rot_xyz(rz=-side * 22), nu=12, squash=(1.0, 0.55), scale=s)
            B.lathe([(0.0, 0), (0.06, 0.0), (0.03, 0.07), (0.0, 0.11)], "accent2", base=(side * 0.215 * s, (top - 0.085) * s, 0.03 * s),
                    rot=rot_xyz(rz=-side * 22), nu=10, squash=(1.0, 0.3), scale=s)
    if "star_tail" in P:
        pts = [(0.0, 0.10, -0.22), (0.06, 0.15, -0.30), (0.12, 0.24, -0.33), (0.14, 0.34, -0.30)]
        for k, (x, y, z) in enumerate(pts):
            B.ellipsoid((x * s, y * s, z * s), (0.055 * s, 0.055 * s, 0.055 * s), "main", nu=10, nv=6)
        B.ellipsoid((0.15 * s, 0.42 * s, -0.28 * s), (0.06 * s, 0.06 * s, 0.03 * s), "goldsoft", nu=10, nv=6)
    if "crystal_ears" in P:
        for side in (-1, 1):
            B.lathe([(0.0, 0), (0.08, 0.0), (0.05, 0.08), (0.0, 0.20)], "accent", base=(side * 0.20 * s, (top - 0.07) * s, 0),
                    rot=rot_xyz(rz=-side * 20), nu=6, scale=s)
            B.lathe([(0.0, 0), (0.04, 0.0), (0.0, 0.10)], "accent2", base=(side * 0.31 * s, (top - 0.13) * s, 0.02 * s),
                    rot=rot_xyz(rz=-side * 50), nu=6, scale=s)
    if "flame_tuft" in P:
        B.lathe([(0.0, 0), (0.13, 0.03), (0.135, 0.09), (0.10, 0.17), (0.05, 0.25), (0.0, 0.36)], "accent", base=(0, (top - 0.08) * s, 0.0),
                rot=rot_xyz(rx=-12), nu=16, scale=s)
        B.lathe([(0.0, 0), (0.08, 0.02), (0.075, 0.08), (0.04, 0.15), (0.0, 0.22)], "accent2", base=(0, (top - 0.06) * s, 0.06 * s),
                rot=rot_xyz(rx=-12), nu=12, scale=s)
    if "moss_tufts" in P:
        rng = np.random.default_rng(9)
        for _ in range(9):
            lon = rng.uniform(-math.pi, math.pi)
            if abs(lon) < 0.9:
                lon = math.copysign(0.9 + abs(lon), lon)
            lat = rng.uniform(0.25, 1.0)
            x = hx * math.cos(lat) * math.sin(lon)
            z = hz * math.cos(lat) * math.cos(lon)
            y = head_y + hy * math.sin(lat)
            r = rng.uniform(0.05, 0.08)
            B.ellipsoid((x * s, y * s, z * s), (r * s, r * 0.7 * s, r * s), "dark", nu=10, nv=6)
    if "mushrooms" in P:
        for (x, z, h, r, tilt) in [(0.10, 0.02, 0.12, 0.10, -12), (-0.15, -0.04, 0.08, 0.07, 18)]:
            B.lathe([(0.0, 0), (0.03, 0.0), (0.025, h), (0.0, h + 0.005)], "accent2", base=(x * s, (top - 0.03) * s, z * s),
                    rot=rot_xyz(rz=tilt), nu=10, scale=s)
            B.lathe([(0.0, 0), (r, 0.0), (r * 0.9, r * 0.35), (r * 0.55, r * 0.7), (0.0, r * 0.8)], "cap",
                    base=((x + math.sin(math.radians(-tilt)) * h) * s, (top - 0.03 + h) * s, z * s), rot=rot_xyz(rz=tilt), nu=16, scale=s)
    if key in MW.CAST:
        MW.build_parts(B, key, c, s, by, head_y, top, sit, plush, props=props, bag=bag)
    return B


# =========================================================================== formats
def build_figure(key, rarity="Rare", height=0.13):
    """A chibi figure on a round collector base. ~13 cm tall."""
    legendary = rarity == "Legendary"
    A = character_atlas(key, legendary=legendary)
    B = Builder(A)
    base_h = 0.012 if rarity in ("Common", "Uncommon") else 0.018
    B.disc_base(0.062 if rarity != "Legendary" else 0.07, base_h, "base_top", "base_side")
    sub = Builder(A)
    build_character(sub, key, height=height)
    B.m.merge(sub.m, translate=(0, base_h, 0))
    return B.m.check(key + "_figure"), A


def build_plush(key, height=0.20):
    A = character_atlas(key, plush=True)
    B = Builder(A)
    build_character(B, key, height=height, pose="sit", plush=True)
    return B.m.check(key + "_plush"), A


def build_monument(key, height=2.6):
    """A giant statue of the character on a stepped pedestal (one tile)."""
    A = character_atlas(key, legendary=True)
    B = Builder(A)
    B.disc_base(0.48, 0.20, "pedestal_top", "pedestal")
    B.disc_base(0.42, 0.18, "pedestal_top", "base_side", y0=0.20)
    sub = Builder(A)
    build_character(sub, key, height=height * 0.82)
    B.m.merge(sub.m, translate=(0, 0.38, 0))
    return B.m.check(key + "_monument"), A


# =========================================================================== renders
def render(m, tex, yaw=-25, pitch=12, size=256, ss=3, bg=None, outline=None, fit=0.86, light=(0.45, 0.75, 0.6),
           frame=None, emissive_u=None):
    """Orthographic render (front = +Z faces the camera at yaw 0). Returns RGBA.
    frame = (cx, cy, span) fixes the framing (turntables); default: fit this view.
    emissive_u: texels with u >= this are drawn unlit (the jt_glow shader's rule)."""
    V = np.array(m.v)
    Nn = np.array(m.n)
    T = np.array(m.t)
    Ry = core._rot("y", -yaw)
    Rx = core._rot("x", pitch)
    R = Rx @ Ry
    P = V @ R.T
    N = Nn @ R.T
    lo, hi = P.min(0), P.max(0)
    span = max(hi[0] - lo[0], hi[1] - lo[1]) / fit
    cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
    if frame is not None:
        cx, cy, span = frame
    W = size * ss
    sc = W / span
    sx = (P[:, 0] - cx) * sc + W / 2
    sy = W / 2 - (P[:, 1] - cy) * sc
    z = P[:, 2]
    img = np.zeros((W, W, 4), np.float32)
    zb = np.full((W, W), -1e9, np.float32)
    C = np.asarray(tex.convert("RGB")).astype(np.float32) / 255
    L = np.array(light, dtype=float)
    L /= np.linalg.norm(L)
    for a, b, c in m.tri:
        xs = np.array([sx[a], sx[b], sx[c]])
        ys = np.array([sy[a], sy[b], sy[c]])
        area = (xs[1] - xs[0]) * (ys[2] - ys[0]) - (xs[2] - xs[0]) * (ys[1] - ys[0])
        if area >= 0:
            continue
        x0, x1 = int(max(0, xs.min())), int(min(W - 1, xs.max() + 1))
        y0, y1 = int(max(0, ys.min())), int(min(W - 1, ys.max() + 1))
        if x1 < x0 or y1 < y0:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        den = (ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2])
        if abs(den) < 1e-9:
            continue
        w0 = ((ys[1] - ys[2]) * (gx - xs[2]) + (xs[2] - xs[1]) * (gy - ys[2])) / den
        w1 = ((ys[2] - ys[0]) * (gx - xs[2]) + (xs[0] - xs[2]) * (gy - ys[2])) / den
        w2 = 1 - w0 - w1
        ins = (w0 >= -1e-4) & (w1 >= -1e-4) & (w2 >= -1e-4)
        zz = w0 * z[a] + w1 * z[b] + w2 * z[c]
        sub = zb[y0:y1 + 1, x0:x1 + 1]
        win = ins & (zz > sub)
        if not win.any():
            continue
        u = w0 * T[a, 0] + w1 * T[b, 0] + w2 * T[c, 0]
        v = w0 * T[a, 1] + w1 * T[b, 1] + w2 * T[c, 1]
        tx = np.clip((u * C.shape[1]).astype(int), 0, C.shape[1] - 1)
        ty = np.clip((v * C.shape[0]).astype(int), 0, C.shape[0] - 1)
        col = C[ty, tx]
        nn = w0[..., None] * N[a] + w1[..., None] * N[b] + w2[..., None] * N[c]
        nn /= np.maximum(1e-6, np.linalg.norm(nn, axis=-1, keepdims=True))
        dif = np.clip(nn @ L, 0, 1)
        rim = np.clip(1 - nn[..., 2], 0, 1) ** 3
        k = 0.62 + 0.45 * dif + 0.10 * rim
        lit = np.clip(col * k[..., None] + 0.05 * rim[..., None], 0, 1)
        if emissive_u is not None:
            col = np.where((u >= emissive_u)[..., None], col, lit)
        else:
            col = lit
        t = img[y0:y1 + 1, x0:x1 + 1]
        t[win, :3] = col[win]
        t[win, 3] = 1
        sub[win] = zz[win]
    im = Image.fromarray((img * 255).astype(np.uint8), "RGBA")
    if outline:
        a = im.split()[3]
        grow = a.filter(ImageFilter.MaxFilter(max(3, (ss * 2) | 1)))
        ol = Image.new("RGBA", im.size, outline + (255,))
        base = Image.new("RGBA", im.size, (0, 0, 0, 0))
        base.paste(ol, mask=grow)
        base.alpha_composite(im)
        im = base
    im = im.resize((size, size), Image.LANCZOS)
    if bg is not None:
        b = Image.new("RGBA", im.size, bg + (255,))
        b.alpha_composite(im)
        im = b
    return im


def turntable(m, tex, frames=16, size=320, pitch=14, fit=0.84, ss=2, yaw0=-22):
    """Frames of the model turning a full circle under a fixed light, all with
    the same framing (centre and scale from the union of every view), so the
    item turns in place. Frame i is at yaw yaw0 + i * 360 / frames."""
    V = np.array(m.v)
    yaws = [yaw0 + i * 360.0 / frames for i in range(frames)]
    lo = np.array([1e9, 1e9])
    hi = -lo
    for y in yaws:
        R = core._rot("x", pitch) @ core._rot("y", -y)
        P = (V @ R.T)[:, :2]
        lo = np.minimum(lo, P.min(0))
        hi = np.maximum(hi, P.max(0))
    span = max(hi[0] - lo[0], hi[1] - lo[1]) / fit
    frame = ((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, span)
    return [render(m, tex, yaw=y, pitch=pitch, size=size, ss=ss, frame=frame) for y in yaws]


def icon(m, tex, outline=(60, 44, 70), yaw=-22, pitch=10):
    """32x32 inventory icon: rendered big, outlined, then shrunk."""
    im = render(m, tex, yaw=yaw, pitch=pitch, size=128, ss=3, outline=outline, fit=0.92)
    return im.resize((32, 32), Image.LANCZOS)


# =========================================================================== more formats
def build_capsule(key, rarity="Common"):
    """A mini character popping out of an open capsule ball (~7 cm): coloured cup
    in front, the clear lid tipped open behind."""
    A = character_atlas(key, legendary=rarity == "Legendary")
    B = Builder(A)
    r = 0.026
    cup = [(0.0, 0.0), (r * 0.55, 0.0015), (r * 0.9, r * 0.3), (r, r * 0.7), (r * 1.02, r * 0.86), (r * 0.9, r * 0.9), (0.0, r * 0.75)]
    B.lathe(cup, "capsule", nu=28)
    lid = [(0.0, 0.0), (r * 0.98, 0.0), (r * 0.92, r * 0.4), (r * 0.66, r * 0.75), (0.0, r * 0.98)]
    B.lathe(lid, "cream", base=(0, r * 0.95, -r * 1.25), rot=rot_xyz(rx=-58), nu=24)
    sub = Builder(A)
    build_character(sub, key, height=0.062)
    B.m.merge(sub.m, translate=(0, r * 0.45, 0.002))
    return B.m.check(key + "_capsule"), A


RARITY_STYLE = {
    "Common": dict(frame=(214, 206, 222), bg=((255, 246, 250), (244, 236, 255)), stars=1),
    "Uncommon": dict(frame=(150, 214, 160), bg=((240, 255, 244), (226, 246, 236)), stars=2),
    "Rare": dict(frame=(120, 170, 240), bg=((236, 246, 255), (222, 232, 255)), stars=3),
    "Epic": dict(frame=(186, 120, 230), bg=((248, 236, 255), (234, 216, 252)), stars=4),
    "Legendary": dict(frame=(236, 178, 54), bg=((255, 248, 220), (255, 230, 178)), stars=5),
}


def portrait(key, size=512, yaw=-14):
    """The character alone (no base), for flat merch. Transparent background."""
    A = character_atlas(key)
    B = Builder(A)
    build_character(B, key, height=1.0)
    return render(B.m, A.img, yaw=yaw, pitch=6, size=size, ss=2, outline=(255, 255, 255), fit=0.9)


def _sparkles(d, W, H, colour, n, seed, rmin=6, rmax=16):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(rmin, rmax)
        pts = []
        for i in range(8):
            rr = r if i % 2 == 0 else r * 0.3
            a = i * math.pi / 4
            pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
        d.polygon(pts, fill=colour)


def card_art(key, rarity, number, series="Series 1", W=480, H=670):
    """Front of a trading card."""
    c = CAST[key]
    st = RARITY_STYLE[rarity]
    im = Image.new("RGBA", (W, H), st["bg"][0] + (255,))
    d = ImageDraw.Draw(im)
    for y in range(H):  # soft vertical gradient
        d.line([(0, y), (W, y)], fill=mix(st["bg"][0], st["bg"][1], y / H) + (255,))
    # a big soft circle in the character's colour behind them
    d.ellipse([W * 0.12, H * 0.14, W * 0.88, H * 0.70], fill=mix(c["accent"], (255, 255, 255), 0.55) + (255,))
    _sparkles(d, W, H, (255, 255, 255, 230), 22 if rarity in ("Epic", "Legendary") else 12, number)
    pic = portrait(key, size=int(W * 0.78))
    im.alpha_composite(pic, (int(W * 0.11), int(H * 0.10)))
    # name plate
    d.rounded_rectangle([W * 0.08, H * 0.75, W * 0.92, H * 0.86], radius=24, fill=(255, 255, 255, 235), outline=st["frame"] + (255,), width=5)
    f = font(40)
    tw = d.textlength(c["name"], font=f)
    d.text(((W - tw) / 2, H * 0.763), c["name"], font=f, fill=mix(c["body"], (40, 24, 60), 0.55) + (255,))
    # rarity stars + series line
    n = st["stars"]
    for i in range(n):
        x = W / 2 + (i - (n - 1) / 2) * 34
        y = H * 0.905
        pts = []
        for k in range(10):
            rr = 14 if k % 2 == 0 else 6
            a = -math.pi / 2 + k * math.pi / 5
            pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
        d.polygon(pts, fill=st["frame"] + (255,))
    f2 = font(20)
    label = "JAMIE'S TREASURES  %s  #%03d" % (series.upper(), number)
    tw = d.textlength(label, font=f2)
    d.text(((W - tw) / 2, H * 0.94), label, font=f2, fill=shade(st["frame"], 0.7) + (255,))
    # frame
    d.rounded_rectangle([6, 6, W - 7, H - 7], radius=30, outline=st["frame"] + (255,), width=14)
    if rarity in ("Rare", "Epic", "Legendary"):  # holo foil sheen
        a = np.asarray(im).astype(np.float32)
        yy, xx = np.mgrid[0:H, 0:W]
        band = (np.sin((xx + yy) / 38.0) * 0.5 + 0.5) ** 6
        tint = np.stack([255 - 60 * np.sin(yy / 90), 230 + 25 * np.sin(xx / 70), 255 - 50 * np.cos(yy / 60)], -1)
        a[..., :3] = a[..., :3] * (1 - 0.18 * band[..., None]) + tint * 0.18 * band[..., None]
        im = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
    return im


def card_back(W=480, H=670):
    im = Image.new("RGBA", (W, H), (190, 172, 240, 255))
    d = ImageDraw.Draw(im)
    for i in range(-H, W + H, 48):
        d.line([(i, 0), (i + H, H)], fill=(204, 188, 246, 255), width=18)
    d.rounded_rectangle([6, 6, W - 7, H - 7], radius=30, outline=(255, 255, 255, 255), width=14)
    d.ellipse([W * 0.2, H * 0.3, W * 0.8, H * 0.3 + W * 0.6], fill=(255, 255, 255, 255))
    f = font(54)
    for k, line in enumerate(["JAMIE'S", "TREASURES"]):
        tw = d.textlength(line, font=f)
        d.text(((W - tw) / 2, H * 0.4 + k * 64), line, font=f, fill=(140, 110, 210, 255))
    _sparkles(d, W, H, (255, 255, 255, 255), 10, 99)
    return im


def build_card(key, rarity, number, series="Series 1"):
    """A trading card lying flat (63 x 88 mm)."""
    A = core.Atlas(1024, background=(255, 255, 255, 255))
    A.add("front", card_art(key, rarity, number, series=series))
    A.add("back", card_back())
    A.add("edge", swatch((250, 250, 250), size=16, grad=False))
    A.finish()
    m = core.Mesh()
    w, h, t = 0.063, 0.088, 0.0012
    # lying flat: x across, z along the card, y up; the art faces up
    top = A.uv("front", rot=0)
    m.box(-w / 2, w / 2, 0.0, t, -h / 2, h / 2, A.uv("edge"), top=_uv_flat(A, "front"), bottom=A.uv("back", rot=2))  # reads upright when the card is flipped over
    return m.check(key + "_card"), A


def _uv_flat(A, name, flip=False):
    """UVs for the top (or bottom) face of a box lying flat, so the picture is upright when seen from the front edge."""
    q = A.uv(name, flip=flip)
    return q


def acrylic_art(key, rarity, W=512, H=640):
    c = CAST[key]
    st = RARITY_STYLE[rarity]
    im = Image.new("RGBA", (W, H), mix(c["accent"], (255, 255, 255), 0.7) + (255,))
    d = ImageDraw.Draw(im)
    for k in range(9):  # polka dots
        for j in range(8):
            x, y = 30 + k * 60 + (j % 2) * 30, 30 + j * 80
            d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=mix(c["accent"], (255, 255, 255), 0.45) + (255,))
    pic = portrait(key, size=int(W * 0.92))
    im.alpha_composite(pic, (int(W * 0.04), int(H * 0.06)))
    d.rounded_rectangle([6, 6, W - 7, H - 7], radius=40, outline=(255, 255, 255, 255), width=12)
    d.rounded_rectangle([18, 18, W - 19, H - 19], radius=32, outline=st["frame"] + (255,), width=5)
    return im


def build_acrylic(key, rarity):
    """An acrylic stand: a printed clear plate on a small base (~10 cm)."""
    c = CAST[key]
    A = core.Atlas(1024, background=(255, 255, 255, 255))
    A.add("art", acrylic_art(key, rarity))
    A.add("clear", swatch((236, 246, 252), size=16, grad=False))
    A.add("base", swatch(mix(c["accent"], (255, 255, 255), 0.3), size=32))
    A.add("label", base_label(key))
    A.finish()
    m = core.Mesh()
    w, h, t = 0.064, 0.080, 0.003
    y0 = 0.010
    m.box(-w / 2, w / 2, y0, y0 + h, -t / 2, t / 2, A.uv("clear"), front=A.uv("art"), back=A.uv("art", flip=True))
    m.box(-0.036, 0.036, 0.0, y0, -0.018, 0.018, A.uv("base"), front=A.uv("label"))
    return m.check(key + "_acrylic"), A


def base_label(key, W=256, H=64):
    c = CAST[key]
    im = Image.new("RGBA", (W, H), mix(c["accent"], (255, 255, 255), 0.3) + (255,))
    d = ImageDraw.Draw(im)
    f = font(28)
    tw = d.textlength(c["name"], font=f)
    d.text(((W - tw) / 2, 12), c["name"], font=f, fill=mix(c["body"], (40, 24, 60), 0.6) + (255,))
    return im


# =========================================================================== bags
def recolour(src, main, shade_floor=0.55):
    """Keeps the vanilla texture's shading and stitch detail, in a new colour."""
    a = np.asarray(src.convert("RGBA")).astype(np.float32)
    L = a[..., :3].mean(-1)
    m = np.median(L)
    k = np.clip(L / max(m, 1), shade_floor, 1.6)
    out = np.empty_like(a)
    out[..., :3] = np.clip(np.array(main, dtype=np.float32)[None, None, :] * k[..., None], 0, 255)
    out[..., 3] = 255
    return Image.fromarray(out.astype(np.uint8), "RGBA")


# Front panel of each vanilla mesh, in texture space (measured from the meshes'
# UV layout, see docs/STYLE_GUIDE.md): centre u, centre v, half width, half height.
BAG_PANEL = {
    "school": (0.345, 0.40, 0.14, 0.22),
    "hydration": (0.32, 0.45, 0.12, 0.28),
}


BAG_MAIN = {"MochiMallow": "accent", "Bunbloom": "accent", "PuddlePaws": "accent"}  # near-white characters use their accent so the bag keeps its shading


def bag_texture(key, src, base, legendary=False, size=512):
    c = CAST[key]
    im = recolour(src, c[BAG_MAIN.get(key, "body")]).resize((size, size), Image.LANCZOS)
    cu, cv, hw, hh = BAG_PANEL[base]
    # face patch painted onto the outer panel, centred on its seam
    S = SS
    layer = Image.new("RGBA", (size * S, size * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    X, Y = cu * size * S, cv * size * S
    R = hw * size * S
    parts = c["parts"]
    if "floppy_ears" in parts:  # ears drooping down both sides of the face
        for side in (-1, 1):
            d.ellipse([X + side * R * 0.95 - R * 0.28, Y - R * 0.55, X + side * R * 0.95 + R * 0.28, Y + R * 1.25], fill=shade(c["body"], 1.25) + (255,))
            d.ellipse([X + side * R * 0.95 - R * 0.15, Y - R * 0.35, X + side * R * 0.95 + R * 0.15, Y + R * 1.05], fill=c["accent2"] + (255,))
    if "cloud_puffs" in parts:
        for k in range(5):
            x = X + (k - 2) * R * 0.42
            d.ellipse([x - R * 0.32, Y - R * 0.95, x + R * 0.32, Y - R * 0.35], fill=c["body"] + (255,))
    d.ellipse([X - R * 0.95, Y - R * 0.55, X + R * 0.95, Y + R * 1.05], fill=(c["belly"] if "cloud_puffs" not in parts else c["body"]) + (255,))
    if "crescent_charm" in parts:
        cx, cy, cr = X + R * 0.55, Y - R * 0.38, R * 0.22
        d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=c["accent"] + (255,))
        d.ellipse([cx - cr * 0.45, cy - cr * 1.15, cx + cr * 1.35, cy + cr * 0.65], fill=(c["belly"]) + (255,))
    if "star_tummy" in parts:
        pass
    for side in (-1, 1):
        ex, ey = X + side * R * 0.42, Y + R * 0.18
        if c["eyes"] in ("sleepy", "happy"):
            d.arc([ex - R * 0.17, ey - R * 0.12, ex + R * 0.17, ey + R * 0.12], 200 if c["eyes"] == "happy" else 20,
                  340 if c["eyes"] == "happy" else 160, fill=c["eye"] + (255,), width=int(R * 0.07))
        else:
            d.ellipse([ex - R * 0.13, ey - R * 0.18, ex + R * 0.13, ey + R * 0.18], fill=c["eye"] + (255,))
            d.ellipse([ex - R * 0.09, ey - R * 0.14, ex - R * 0.01, ey - R * 0.05], fill=(255, 255, 255, 255))
        d.ellipse([X + side * R * 0.7 - R * 0.12, Y + R * 0.42 - R * 0.07, X + side * R * 0.7 + R * 0.12, Y + R * 0.42 + R * 0.07],
                  fill=c["blush_c"] + (255,))
    d.arc([X - R * 0.10, Y + R * 0.30, X + R * 0.10, Y + R * 0.46], 20, 160, fill=c["eye"] + (255,), width=int(R * 0.05))
    if legendary:  # gold stars around the panel
        for k in range(6):
            a = -math.pi / 2 + TAU * k / 6
            x, y = X + math.cos(a) * R * 1.2, Y + R * 0.2 + math.sin(a) * hh * size * S * 0.85
            pts = []
            for i in range(10):
                rr = R * 0.22 if i % 2 == 0 else R * 0.09
                aa = -math.pi / 2 + i * math.pi / 5
                pts.append((x + rr * math.cos(aa), y + rr * math.sin(aa)))
            d.polygon(pts, fill=(246, 196, 72, 255))
    layer = layer.resize((size, size), Image.LANCZOS)
    im.alpha_composite(layer)
    return im


def bag_mesh_from_x(path):
    """The vanilla bag mesh (bind pose) as a core.Mesh, only for icons and previews."""
    sys.path.insert(0, os.path.join(HERE, ".."))
    from xmesh import parse
    V, F, T = parse(path)
    m = core.Mesh()
    for f in F:
        for a in range(1, len(f) - 1):
            ids = [f[0], f[a], f[a + 1]]
            P = V[ids]
            g = np.cross(P[1] - P[0], P[2] - P[0])
            n = np.linalg.norm(g)
            if n < 1e-12:
                continue
            g /= n
            b = len(m.v)
            for k in ids:
                m.v.append(np.array(V[k], dtype=float))
                m.n.append(g)
                m.t.append((float(T[k][0]), float(T[k][1])))
            m.tri.append((b, b + 1, b + 2))
    return m


# =========================================================================== furniture
def shelf_atlas():
    A = core.Atlas(512, background=(255, 240, 246, 255))
    A.add("wood", swatch((255, 226, 236), size=64))
    A.add("trim", swatch((196, 178, 245), size=64))
    back = Image.new("RGBA", (128, 128), (255, 246, 250, 255))
    d = ImageDraw.Draw(back)
    for i in range(4):
        for j in range(4):
            x, y = 16 + i * 32 + (j % 2) * 16, 16 + j * 32
            d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(250, 214, 230, 255))
    A.add("back", back)
    crest = Image.new("RGBA", (256 * SS, 96 * SS), (196, 178, 245, 255))
    d = ImageDraw.Draw(crest)
    f = font(30 * SS)
    t = "Jamie's Treasures"
    tw = d.textlength(t, font=f)
    d.text(((256 * SS - tw) / 2, 22 * SS), t, font=f, fill=(255, 255, 255, 255))
    _sparkles(d, 256 * SS, 96 * SS, (255, 236, 160, 255), 8, 4, rmin=10, rmax=22)
    A.add("crest", crest.resize((256, 96), Image.LANCZOS))
    return A.finish()


def build_shelf(surfaces_px, px_per_m):
    """Open-front collector's shelf, one tile, front = +Z. Board TOPS sit exactly
    at the tile Surface heights, so placed items rest on the boards."""
    A = shelf_atlas()
    m = core.Mesh()
    W, D = 0.46, 0.27            # half width, half depth
    side_t, board_t = 0.03, 0.025
    tops = [p / px_per_m for p in surfaces_px]
    H = tops[-1] + 0.30          # back panel and sides rise above the top board
    wood, trim = A.uv("wood"), A.uv("trim")
    # sides
    m.box(-W, -W + side_t, 0, H, -D, D, wood, top=trim)
    m.box(W - side_t, W, 0, H, -D, D, wood, top=trim)
    # back panel
    m.box(-W + side_t, W - side_t, 0, H, -D, -D + 0.015, A.uv("back"))
    # plinth under the bottom board
    m.box(-W + side_t, W - side_t, 0, tops[0] - board_t, D - 0.03, D, trim)
    # boards
    for top in tops:
        m.box(-W + side_t, W - side_t, top - board_t, top, -D + 0.015, D, wood, front=trim)
    # crest over the top (with the name)
    m.box(-W, W, H, H + 0.11, -D, -D + 0.04, trim, front=A.uv("crest"))
    return m.check("shelf"), A


# =========================================================================== Series 2: Fiesta
FIESTA_PALETTE = [(244, 96, 120), (255, 204, 80), (110, 190, 240), (130, 210, 130), (196, 150, 240), (255, 150, 90)]


def _stripes(colours, size=64, horizontal=True):
    im = Image.new("RGBA", (size, size), colours[0] + (255,))
    d = ImageDraw.Draw(im)
    n = len(colours)
    for i, c in enumerate(colours):
        if horizontal:
            d.rectangle([0, i * size // n, size, (i + 1) * size // n], fill=c + (255,))
        else:
            d.rectangle([i * size // n, 0, (i + 1) * size // n, size], fill=c + (255,))
    return im


def _text_sign(text, bg, fg, W=256, H=128):
    im = Image.new("RGBA", (W * SS, H * SS), bg + (255,))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([6 * SS, 6 * SS, (W - 6) * SS, (H - 6) * SS], radius=14 * SS, outline=fg + (255,), width=5 * SS)
    f = font(int(H * 0.42) * SS)
    tw = d.textlength(text, font=f)
    d.text(((W * SS - tw) / 2, H * SS * 0.22), text, font=f, fill=fg + (255,))
    return im.resize((W, H), Image.LANCZOS)


def _ball():
    im = Image.new("RGBA", (128, 64), (240, 130, 50, 255))
    d = ImageDraw.Draw(im)
    for x in (32, 64, 96):
        d.line([(x, 0), (x, 64)], fill=(70, 40, 30, 255), width=2)
    d.line([(0, 32), (128, 32)], fill=(70, 40, 30, 255), width=2)
    return im


def PROP_SWATCHES():
    return {
        "silver": swatch((210, 214, 222)),
        "wood": swatch((176, 124, 82)),
        "darkwood": swatch((120, 82, 56)),
        "white": swatch((250, 250, 250)),
        "red": swatch((226, 60, 70)),
        "yellow": swatch((255, 210, 70)),
        "black": swatch((50, 48, 56)),
        "pinkprop": swatch((246, 150, 180)),
        "lechon": swatch((206, 120, 60)),
        "cone": swatch((222, 170, 100)),
        "ube": swatch((150, 100, 190)),
        "rope": swatch((210, 190, 150)),
        "halohalo": _stripes([(255, 236, 160), (250, 250, 250), (196, 150, 230), (210, 120, 110), (150, 100, 190)]),
        "bunting": _stripes(FIESTA_PALETTE, horizontal=False),
        "sign": _text_sign("CUBAO", (255, 220, 90), (60, 40, 30)),
        "ball": _ball(),
        "sashtext": _text_sign("KAPITAN", (246, 196, 72), (110, 60, 20)),
        "musetext": _text_sign("MUSE", (250, 120, 160), (255, 255, 255)),
        "fiesta_top": fiesta_base_top(False),
        "fiesta_top_gold": fiesta_base_top(True),
    }


def fiesta_base_top(gold, size=128):
    S = size * SS
    im = Image.new("RGBA", (S, S), (255, 248, 236, 255) if not gold else (255, 232, 160, 255))
    d = ImageDraw.Draw(im)
    n = 18
    for k in range(n):  # banderitas around the rim
        a0 = TAU * k / n
        a1 = TAU * (k + 0.5) / n
        am = (a0 + a1) / 2
        r0, r1 = S * 0.47, S * 0.36
        c = FIESTA_PALETTE[k % len(FIESTA_PALETTE)] if not gold else (226, 170, 50)
        d.polygon([(S / 2 + r0 * math.cos(a0), S / 2 + r0 * math.sin(a0)), (S / 2 + r0 * math.cos(a1), S / 2 + r0 * math.sin(a1)),
                   (S / 2 + r1 * math.cos(am), S / 2 + r1 * math.sin(am))], fill=c + (255,))
    return im.resize((size, size), Image.LANCZOS)


def _star_prism(m, A, region, centre, r, depth, inner=0.45, points=5):
    """A flat star with thickness, facing +Z."""
    cx, cy, cz = centre
    pts = []
    for i in range(points * 2):
        rr = r if i % 2 == 0 else r * inner
        a = math.pi / 2 + i * math.pi / points
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    uv = A.point(region, 0.5, 0.5)
    for zz, sign in ((cz + depth / 2, 1), (cz - depth / 2, -1)):
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            tri = [(cx, cy, zz), (a[0], a[1], zz), (b[0], b[1], zz)]
            if sign < 0:
                tri = [tri[0], tri[2], tri[1]]
            m.triangle(tri, [uv, uv, uv])
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        m.quad([(b[0], b[1], cz - depth / 2), (a[0], a[1], cz - depth / 2), (a[0], a[1], cz + depth / 2), (b[0], b[1], cz + depth / 2)],
               [uv, uv, uv, uv])


def _flag(m, A, region_u, p0, p1, drop):
    """One triangle pennant hanging from the string between p0 and p1 (two-sided)."""
    mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 - drop, (p0[2] + p1[2]) / 2)
    uv = A.point("bunting", region_u, 0.5)
    m.triangle([p0, mid, p1], [uv, uv, uv], two_sided=True)


FIESTA_THEMES = {
    # theme: (title, character)
    "Taho": "Taho Vendor",
    "HaloHalo": "Halo-Halo Stand",
    "Barker": "Jeepney Barker",
    "Duyan": "Siesta in the Duyan",
    "Muse": "Fiesta Muse",
    "Parol": "Parol Maker",
    "Lechon": "Lechon Master",
    "Sorbetes": "Sorbetero",
    "Videoke": "Videoke Star",
    "Banderitas": "Banderitas",
    "Liga": "Liga MVP",
    "Kapitan": "Golden Kapitan",
}
FIESTA_THEMES.update(MW.FIESTA_THEMES)


def build_fiesta(key, theme, rarity="Common", height=0.13):
    """A Fiesta Series figure: the character, a fiesta prop, on a banderitas base."""
    legendary = rarity == "Legendary"
    A = character_atlas(key, legendary=legendary)
    B = Builder(A)
    base_r = {"Duyan": 0.11, "Lechon": 0.09}.get(theme, MW.FIESTA_BASE_R.get(theme, 0.075))
    base_h = 0.016
    B.disc_base(base_r, base_h, "fiesta_top_gold" if legendary else "fiesta_top", "base_side")
    pose = "sit" if theme in ("Duyan", "Lechon") else MW.FIESTA_POSE.get(theme)
    sub = Builder(A)
    lift = 0.0
    if theme == "Duyan":
        lift = 0.14 * height   # lies IN the hammock
    build_character(sub, key, height=height, pose=pose, props=False)
    B.m.merge(sub.m, translate=(0, base_h + lift, 0))
    s = height
    y0 = base_h
    P = Builder(A)
    m = P.m
    hand = (0.30 * s, y0 + 0.30 * s, 0.10 * s)   # right hand, in front
    if theme == "Taho":
        m.bar((-0.62 * s, y0 + 0.50 * s, 0.0), (0.62 * s, y0 + 0.50 * s, 0.0), 0.02 * s, 0.02 * s, A.uv("wood"))
        for side in (-1, 1):
            x = side * 0.56 * s
            P.lathe([(0.0, 0.0), (0.10, 0.0), (0.115, 0.17), (0.0, 0.18)], "silver", base=(x, y0, 0.0), nu=18, scale=s)
            m.bar((x, y0 + 0.18 * s, 0.0), (x, y0 + 0.50 * s, 0.0), 0.008 * s, 0.008 * s, A.uv("rope"))
    elif theme == "HaloHalo":
        P.lathe([(0.0, 0.0), (0.06, 0.0), (0.075, 0.20), (0.0, 0.205)], "halohalo", base=(hand[0] - 0.06 * s, y0 + 0.16 * s, hand[2] + 0.10 * s), nu=18, scale=s)
        P.ellipsoid((hand[0] - 0.06 * s, y0 + 0.37 * s, hand[2] + 0.10 * s), (0.07 * s, 0.04 * s, 0.07 * s), "white", nu=14, nv=8)
        m.bar((hand[0] - 0.03 * s, y0 + 0.35 * s, hand[2] + 0.10 * s), (hand[0] + 0.02 * s, y0 + 0.52 * s, hand[2] + 0.08 * s), 0.012 * s, 0.006 * s, A.uv("silver"))
    elif theme == "Barker":
        m.bar((0.32 * s, y0 + 0.20 * s, 0.06 * s), (0.36 * s, y0 + 1.02 * s, 0.06 * s), 0.02 * s, 0.02 * s, A.uv("wood"))
        m.box(0.14 * s, 0.58 * s, y0 + 0.96 * s, y0 + 1.18 * s, 0.05 * s, 0.075 * s, A.uv("yellow"), front=A.uv("sign"), back=A.uv("sign", flip=True))
        P.ellipsoid((-0.20 * s, y0 + 0.52 * s, 0.02 * s), (0.10 * s, 0.03 * s, 0.13 * s), "white", rot=rot_xyz(rz=25), nu=12, nv=6)
    elif theme == "Duyan":
        P.ellipsoid((0, y0 + 0.17 * s, 0.02 * s), (0.62 * s, 0.08 * s, 0.32 * s), "bunting", nu=28, nv=10)
        for side in (-1, 1):
            m.bar((side * 0.80 * s, y0, -0.05 * s), (side * 0.80 * s, y0 + 0.62 * s, -0.05 * s), 0.05 * s, 0.05 * s, A.uv("darkwood"))
            m.bar((side * 0.80 * s, y0 + 0.58 * s, -0.05 * s), (side * 0.58 * s, y0 + 0.20 * s, 0.0), 0.012 * s, 0.012 * s, A.uv("rope"))
    elif theme == "Muse":
        m.bar((-0.20 * s, y0 + 0.43 * s, 0.245 * s), (0.20 * s, y0 + 0.10 * s, 0.245 * s), 0.09 * s, 0.012 * s, A.uv("pinkprop"), up=(0, 0, 1))
        top = y0 + (0.66 + c_head_y(key)) * s
        for k in range(9):
            a = TAU * k / 9
            col = ["pinkprop", "white", "yellow"][k % 3]
            P.ellipsoid((0.27 * math.sin(a) * s, top - 0.02 * s, 0.24 * math.cos(a) * s), (0.05 * s, 0.04 * s, 0.05 * s), col, nu=10, nv=6)
    elif theme == "Parol":
        m.bar((0.30 * s, y0 + 0.25 * s, 0.10 * s), (0.42 * s, y0 + 1.05 * s, 0.10 * s), 0.018 * s, 0.018 * s, A.uv("wood"))
        _star_prism(m, A, "red", (0.44 * s, y0 + 1.15 * s, 0.10 * s), 0.17 * s, 0.05 * s)
        _star_prism(m, A, "yellow", (0.44 * s, y0 + 1.15 * s, 0.13 * s), 0.09 * s, 0.02 * s)
    elif theme == "Lechon":
        cx, cy, cz = 0.0, y0 + 0.20 * s, 0.42 * s
        P.ellipsoid((cx, cy, cz), (0.30 * s, 0.14 * s, 0.15 * s), "lechon", nu=22, nv=12)
        P.ellipsoid((cx + 0.29 * s, cy + 0.02 * s, cz), (0.10 * s, 0.085 * s, 0.085 * s), "lechon", nu=14, nv=8)
        P.ellipsoid((cx + 0.39 * s, cy, cz), (0.045 * s, 0.045 * s, 0.045 * s), "red", nu=10, nv=6)
        m.bar((cx - 0.50 * s, cy, cz), (cx + 0.50 * s, cy, cz), 0.02 * s, 0.02 * s, A.uv("silver"))
        for side in (-1, 1):
            m.bar((side * 0.46 * s, y0, cz), (side * 0.46 * s, cy + 0.03 * s, cz), 0.03 * s, 0.03 * s, A.uv("darkwood"))
    elif theme == "Sorbetes":
        P.lathe([(0.0, 0.0), (0.06, 0.18)], "cone", base=(hand[0], y0 + 0.24 * s, hand[2] + 0.06 * s), nu=14, scale=s)
        for k, (col, dy) in enumerate((("pinkprop", 0.0), ("ube", 0.07), ("yellow", 0.135))):
            P.ellipsoid((hand[0], y0 + (0.45 + dy) * s, hand[2] + 0.06 * s), (0.065 * s, 0.055 * s, 0.065 * s), col, nu=14, nv=8)
    elif theme == "Videoke":
        mx, my, mz = 0.14 * s, y0 + 0.55 * s, 0.30 * s
        m.bar((0.28 * s, y0 + 0.30 * s, 0.12 * s), (mx, my, mz), 0.03 * s, 0.03 * s, A.uv("black"))
        P.ellipsoid((mx, my, mz), (0.045 * s, 0.045 * s, 0.045 * s), "silver", nu=12, nv=8)
        m.box(-0.62 * s, -0.36 * s, y0, y0 + 0.36 * s, -0.12 * s, 0.10 * s, A.uv("black"), front=A.uv("darkwood"))
        P.ellipsoid((-0.49 * s, y0 + 0.18 * s, 0.10 * s), (0.08 * s, 0.08 * s, 0.01 * s), "silver", nu=14, nv=6)
    elif theme == "Banderitas":
        pts = []
        for i in range(9):
            t = i / 8.0
            x = (-0.55 + 1.10 * t) * s
            y = y0 + (0.70 + 0.10 * math.sin(math.pi * t)) * s
            pts.append((x, y, 0.22 * s))
        for i in range(8):
            m.bar(pts[i], pts[i + 1], 0.008 * s, 0.008 * s, A.uv("rope"))
            _flag(m, A, (i % 6 + 0.5) / 6, pts[i], pts[i + 1], 0.13 * s)
        for side in (-1, 1):
            m.bar((side * 0.29 * s, y0 + 0.30 * s, 0.10 * s), (side * 0.55 * s, y0 + 0.70 * s, 0.22 * s), 0.015 * s, 0.015 * s, A.uv("wood"))
    elif theme == "Liga":
        P.ellipsoid((hand[0] + 0.02 * s, y0 + 0.42 * s, hand[2] + 0.08 * s), (0.12 * s, 0.12 * s, 0.12 * s), "ball", nu=18, nv=12)
    elif theme in MW.FIESTA_THEMES:
        sit = (pose or CAST[key]["pose"]) == "sit"
        MW.fiesta_prop(P, theme, key, CAST[key], s, y0, hand, (0.60 if sit else 0.66) + c_head_y(key))
    elif theme == "Kapitan":
        m.bar((-0.20 * s, y0 + 0.43 * s, 0.245 * s), (0.20 * s, y0 + 0.10 * s, 0.245 * s), 0.10 * s, 0.012 * s, A.uv("gold"), up=(0, 0, 1))
        top = y0 + (0.66 + c_head_y(key)) * s
        for k in range(5):  # little crown
            a = TAU * k / 5
            P.lathe([(0.0, 0.0), (0.04, 0.0), (0.0, 0.10)], "gold", base=(0.12 * math.sin(a) * s, top - 0.03 * s, 0.12 * math.cos(a) * s), nu=6, scale=s)
        P.lathe([(0.0, 0.0), (0.15, 0.0), (0.15, 0.03), (0.0, 0.03)], "gold", base=(0, top - 0.04 * s, 0), nu=20, scale=s)
    B.m.merge(P.m)
    return B.m.check(key + "_fiesta_" + theme), A


def c_head_y(key):
    return CAST[key]["head"][1]


def blindbox_art(series_title="FIESTA", W=256, H=256):
    im = Image.new("RGBA", (W * SS, H * SS), (255, 240, 248, 255))
    d = ImageDraw.Draw(im)
    S = SS
    for k in range(12):
        x0 = k * W * S / 12
        d.polygon([(x0, 0), (x0 + W * S / 12, 0), (x0 + W * S / 24, 22 * S)], fill=FIESTA_PALETTE[k % 6] + (255,))
    f = font(30 * S)
    for i, line in enumerate(["Jamie's", "Treasures"]):
        tw = d.textlength(line, font=f)
        d.text(((W * S - tw) / 2, (34 + i * 32) * S), line, font=f, fill=(120, 86, 190, 255))
    d.ellipse([(W / 2 - 46) * S, 108 * S, (W / 2 + 46) * S, 200 * S], fill=(255, 255, 255, 255), outline=(196, 178, 245, 255), width=5 * S)
    f2 = font(70 * S)
    tw = d.textlength("?", font=f2)
    d.text(((W * S - tw) / 2, 112 * S), "?", font=f2, fill=(244, 96, 120, 255))
    f3 = font(22 * S)
    t = series_title + " SERIES"
    tw = d.textlength(t, font=f3)
    d.rounded_rectangle([(W * S - tw) / 2 - 12 * S, 210 * S, (W * S + tw) / 2 + 12 * S, 242 * S], radius=12 * S, fill=(244, 96, 120, 255))
    d.text(((W * S - tw) / 2, 212 * S), t, font=f3, fill=(255, 255, 255, 255))
    return im.resize((W, H), Image.LANCZOS)


def build_blindbox():
    A = core.Atlas(512, background=(255, 255, 255, 255))
    A.add("front", blindbox_art())
    A.add("side", _stripes(FIESTA_PALETTE, size=64, horizontal=False))
    A.add("top", swatch((196, 178, 245), size=64))
    A.finish()
    m = core.Mesh()
    w, h, d = 0.07, 0.09, 0.07
    m.box(-w / 2, w / 2, 0, h, -d / 2, d / 2, A.uv("side"), top=A.uv("top"), front=A.uv("front"), back=A.uv("front"))
    return m.check("blindbox"), A


def journal_cover(W=256, H=320):
    im = Image.new("RGBA", (W * SS, H * SS), (196, 178, 245, 255))
    d = ImageDraw.Draw(im)
    S = SS
    d.rounded_rectangle([12 * S, 12 * S, (W - 12) * S, (H - 12) * S], radius=18 * S, outline=(255, 255, 255, 255), width=6 * S)
    f = font(28 * S)
    for i, line in enumerate(["Collection", "Journal"]):
        tw = d.textlength(line, font=f)
        d.text(((W * S - tw) / 2, (40 + i * 34) * S), line, font=f, fill=(255, 255, 255, 255))
    _sparkles(d, W * S, H * S, (255, 236, 160, 255), 10, 8, rmin=8 * S, rmax=16 * S)
    return im.resize((W, H), Image.LANCZOS)


def build_journal():
    A = core.Atlas(512, background=(255, 255, 255, 255))
    pic = journal_cover()
    star = portrait("MochiMallow", size=150)
    pic.alpha_composite(star, (53, 135))
    A.add("cover", pic)
    A.add("pages", swatch((252, 248, 236), size=32))
    A.add("spine", swatch((150, 120, 210), size=32))
    A.finish()
    m = core.Mesh()
    w, h, t = 0.16, 0.21, 0.025
    m.box(-w / 2, w / 2, 0.0, t, -h / 2, h / 2, A.uv("pages"), top=A.uv("cover"), left=A.uv("spine"), bottom=A.uv("spine"))
    return m.check("journal"), A
