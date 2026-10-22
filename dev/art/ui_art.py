"""UI pieces for the Collection Journal screen (window + JPhone app).

All drawn here, white on transparent so the game can tint them:
  jt_corner_tl/tr/bl/br  quarter circles for rounded rectangles (32 px)
  jt_circle              a disc (64 px)
  jt_check               a tick (64 px)
  jt_plus                a plus (64 px)
  jt_star                a five point star (64 px)
plus, in full colour:
  jph_app_journal        the JPhone home-screen icon (128 px, same look as
                         JPhone's own icons: glossy rounded square, cream glyph)
"""
import math
from PIL import Image, ImageDraw, ImageFilter

SS = 4  # supersampling


def _canvas(n):
    return Image.new("RGBA", (n * SS, n * SS), (0, 0, 0, 0))


def _down(im, n):
    return im.resize((n, n), Image.LANCZOS)


def corner(which, n=32):
    im = _canvas(n)
    d = ImageDraw.Draw(im)
    N = n * SS
    cx = N if which in ("tl", "bl") else 0
    cy = N if which in ("tl", "tr") else 0
    d.ellipse([cx - N, cy - N, cx + N, cy + N], fill=(255, 255, 255, 255))
    return _down(im, n)


def circle(n=64):
    im = _canvas(n)
    ImageDraw.Draw(im).ellipse([0, 0, n * SS - 1, n * SS - 1], fill=(255, 255, 255, 255))
    return _down(im, n)


def check(n=64):
    im = _canvas(n)
    d = ImageDraw.Draw(im)
    N = n * SS
    pts = [(0.20 * N, 0.52 * N), (0.42 * N, 0.73 * N), (0.80 * N, 0.30 * N)]
    d.line(pts, fill=(255, 255, 255, 255), width=int(0.15 * N), joint="curve")
    for p in (pts[0], pts[2]):
        r = 0.075 * N
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=(255, 255, 255, 255))
    return _down(im, n)


def plus(n=64):
    im = _canvas(n)
    d = ImageDraw.Draw(im)
    N = n * SS
    t = 0.16 * N
    d.rounded_rectangle([0.18 * N, N / 2 - t / 2, 0.82 * N, N / 2 + t / 2], radius=t / 2, fill=(255, 255, 255, 255))
    d.rounded_rectangle([N / 2 - t / 2, 0.18 * N, N / 2 + t / 2, 0.82 * N], radius=t / 2, fill=(255, 255, 255, 255))
    return _down(im, n)


def _star_pts(cx, cy, ro, ri, rot=-90):
    pts = []
    for i in range(10):
        r = ro if i % 2 == 0 else ri
        a = math.radians(rot + i * 36)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def star(n=64):
    im = _canvas(n)
    N = n * SS
    ImageDraw.Draw(im).polygon(_star_pts(N / 2, N * 0.54, N * 0.48, N * 0.21), fill=(255, 255, 255, 255))
    return _down(im, n)


def app_icon(n=128):
    """Lilac glossy tile with a cream sticker book, a gold star sticker and a heart."""
    N = n * SS
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    # tile: vertical gradient, rounded
    top, bot = (196, 158, 246), (128, 86, 210)
    grad = Image.new("RGBA", (N, N))
    gd = ImageDraw.Draw(grad)
    for y in range(N):
        t = y / (N - 1)
        gd.line([(0, y), (N, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)) + (255,))
    mask = Image.new("L", (N, N), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, N - 1, N - 1], radius=int(N * 0.23), fill=255)
    im.paste(grad, (0, 0), mask)
    # gloss on the top half
    gloss = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    gl = ImageDraw.Draw(gloss)
    gl.rounded_rectangle([int(N * 0.04), int(N * 0.03), int(N * 0.96), int(N * 0.46)], radius=int(N * 0.2),
                         fill=(255, 255, 255, 46))
    gm = Image.new("L", (N, N), 0)
    gm.paste(mask, (0, 0))
    im.alpha_composite(Image.composite(gloss, Image.new("RGBA", (N, N), (0, 0, 0, 0)), gm))
    d = ImageDraw.Draw(im)
    cream = (252, 244, 222, 255)
    ink = (110, 70, 180, 255)
    # shadow under the book
    sh = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([int(N * 0.25), int(N * 0.25), int(N * 0.79), int(N * 0.83)],
                                         radius=int(N * 0.07), fill=(60, 30, 110, 90))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(N * 0.02)))
    d = ImageDraw.Draw(im)
    # the book: cover + spine
    x0, y0, x1, y1 = N * 0.24, N * 0.20, N * 0.76, N * 0.78
    d.rounded_rectangle([x0, y0, x1, y1], radius=int(N * 0.06), fill=cream)
    d.rounded_rectangle([x0, y0, x0 + N * 0.09, y1], radius=int(N * 0.05), fill=(232, 214, 250, 255))
    d.line([(x0 + N * 0.09, y0 + N * 0.02), (x0 + N * 0.09, y1 - N * 0.02)], fill=(200, 176, 236, 255),
           width=int(N * 0.012))
    # sticker spots on the cover: a gold star, a pink heart, a mint dot
    cx, cy = N * 0.535, N * 0.43
    d.polygon(_star_pts(cx, cy, N * 0.135, N * 0.06), fill=(246, 196, 72, 255))
    d.polygon(_star_pts(cx, cy, N * 0.105, N * 0.045), fill=(255, 216, 110, 255))
    hx, hy, hr = N * 0.62, N * 0.645, N * 0.05
    d.ellipse([hx - hr * 2, hy - hr, hx, hy + hr], fill=(240, 110, 150, 255))
    d.ellipse([hx, hy - hr, hx + hr * 2, hy + hr], fill=(240, 110, 150, 255))
    d.polygon([(hx - hr * 1.95, hy + hr * 0.25), (hx + hr * 1.95, hy + hr * 0.25), (hx, hy + hr * 2.3)],
              fill=(240, 110, 150, 255))
    mr = N * 0.04
    d.ellipse([N * 0.43 - mr, N * 0.655 - mr, N * 0.43 + mr, N * 0.655 + mr], fill=(130, 214, 180, 255))
    # bookmark ribbon
    d.polygon([(N * 0.66, y0), (N * 0.72, y0), (N * 0.72, y0 + N * 0.13), (N * 0.69, y0 + N * 0.105),
               (N * 0.66, y0 + N * 0.13)], fill=ink)
    return im.resize((n, n), Image.LANCZOS)


def write_all(out_dir_ui, out_app=None):
    import os
    os.makedirs(out_dir_ui, exist_ok=True)
    for w in ("tl", "tr", "bl", "br"):
        corner(w).save(os.path.join(out_dir_ui, "jt_corner_%s.png" % w))
    circle().save(os.path.join(out_dir_ui, "jt_circle.png"))
    check().save(os.path.join(out_dir_ui, "jt_check.png"))
    plus().save(os.path.join(out_dir_ui, "jt_plus.png"))
    star().save(os.path.join(out_dir_ui, "jt_star.png"))
    if out_app:
        os.makedirs(os.path.dirname(out_app), exist_ok=True)
        app_icon().save(out_app)


# --------------------------------------------------------------------------- inspect turntables
STAGE_IN = (74, 60, 110)    # centre of the stage (lilac)
STAGE_OUT = (23, 18, 34)    # edge = the window's screen colour


def inspect_frames(frames):
    """Turntable frames (RGBA, same size) -> the Inspect window's frames: each
    on the same lilac stage with one soft floor shadow (from all frames
    together, so it doesn't jump), dithered to a 256-colour PNG palette
    (about a third of the size; the game reads palette PNGs)."""
    import numpy as np
    S = frames[0].size[0]
    yy, xx = np.mgrid[0:S, 0:S]
    d = np.sqrt(((xx - S / 2) / (S * 0.72)) ** 2 + ((yy - S * 0.40) / (S * 0.72)) ** 2)
    t = np.clip(d, 0, 1)[..., None]
    bg = (np.array(STAGE_IN) * (1 - t) + np.array(STAGE_OUT) * t).astype(np.uint8)
    stage = Image.fromarray(bg, "RGB").convert("RGBA")
    # shadow from where the item touches the floor, across every frame
    alpha = np.zeros((S, S), np.uint8)
    for f in frames:
        alpha = np.maximum(alpha, np.array(f)[..., 3])
    ys = np.where(alpha.max(1) > 0)[0]
    xs = np.where(alpha.max(0) > 0)[0]
    if len(ys):
        bottom = ys.max()
        w = xs.max() - xs.min()
        cx = (xs.max() + xs.min()) / 2
        sh = Image.new("L", (S, S), 0)
        ImageDraw.Draw(sh).ellipse([cx - w * 0.46, bottom - S * 0.045, cx + w * 0.46, bottom + S * 0.03], fill=130)
        sh = sh.filter(ImageFilter.GaussianBlur(S * 0.025))
        stage.paste(Image.new("RGBA", (S, S), (8, 5, 16, 255)), mask=sh)
    out = []
    for f in frames:
        im = stage.copy()
        im.alpha_composite(f)
        out.append(im.convert("RGB").quantize(colors=256, method=Image.Quantize.MEDIANCUT,
                                              dither=Image.Dither.FLOYDSTEINBERG))
    return out
