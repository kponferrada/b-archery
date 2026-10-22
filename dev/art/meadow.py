"""Jamie's Treasures - the Meadow friends (16 characters added in 0.3.0).

Same chibi base and style guide as the original cast (kawaii.py). This file
holds their data, their silhouette parts, their painted marks and signature
blushes, and their 16 Fiesta Series props. kawaii.py calls in here; nothing
here imports kawaii (it would load a second copy of it).

Every design is original, made for this mod from Jamie's character briefs.
"""
import math

import numpy as np
from PIL import Image, ImageDraw

import core

TAU = 2 * math.pi


def rot_xyz(rx=0, ry=0, rz=0):
    return core._rot("y", ry) @ core._rot("x", rx) @ core._rot("z", rz)


def align_y(d):
    """Rotation that turns +Y onto direction d."""
    d = np.asarray(d, dtype=float)
    d = d / np.linalg.norm(d)
    y = np.array([0.0, 1.0, 0.0])
    c = float(y @ d)
    if c < -0.9999:
        return core._rot("x", 180)
    v = np.cross(y, d)
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx * (1.0 / (1.0 + c))


# =========================================================================== the cast
# Fields as in kawaii.CAST, plus:
#   arms   False = no arms (the birds get wings from their parts instead)
#   feet   atlas region for the feet (default: "dark" standing, "belly" sitting)
#   held   parts that are a held object (left off in the Fiesta figures, where the prop takes the hands)
CAST = {
    "AcornBean": dict(
        name="Acorn Bean", personality="baby squirrel, never lets go of its one precious nut",
        body=(204, 134, 86), belly=(252, 234, 210), accent=(142, 98, 64), accent2=(226, 176, 108),
        eye=(82, 48, 34), blush_c=(255, 150, 130), eyes="round", mouth="open", blush="acorn",
        head=(0.38, 0.32, 0.33), parts=["face_mask", "squirrel_ears", "acorn_cap", "bushy_tail", "held_nut"], pose="sit",
        held=["held_nut"],
    ),
    "Fernie": dict(
        name="Fernie", personality="gentle little deer, tucks a fresh flower behind one ear every morning",
        body=(196, 140, 98), belly=(250, 236, 214), accent=(104, 172, 88), accent2=(255, 168, 190),
        eye=(74, 46, 40), blush_c=(255, 236, 214), eyes="round", mouth="smile", blush="freckle",
        head=(0.37, 0.31, 0.33), parts=["muzzle", "deer_ears", "fern_antlers", "ear_flower", "deer_spots"], pose="stand",
    ),
    "Bunbloom": dict(
        name="Bunbloom", personality="flower-crowned bunny, its tulip ears open wider when it's happy",
        body=(255, 226, 236), belly=(255, 246, 248), accent=(246, 116, 158), accent2=(126, 194, 106),
        eye=(110, 50, 80), blush_c=(255, 150, 182), eyes="happy", mouth="w", blush="tulip",
        head=(0.37, 0.32, 0.33), parts=["face_mask", "tulip_ears", "flower_crown", "puff_tail"], pose="stand",
    ),
    "CloverCub": dict(
        name="Clover Cub", personality="lucky little bear, finds four-leaf clovers everywhere it naps",
        body=(184, 228, 192), belly=(244, 252, 236), accent=(70, 160, 86), accent2=(246, 196, 72),
        eye=(46, 76, 52), blush_c=(255, 170, 160), eyes="round", mouth="open", blush="clover",
        head=(0.38, 0.32, 0.33), parts=["bear_ears_small", "muzzle", "clover_paws", "lucky_charm"], pose="sit",
    ),
    "Nibblefox": dict(
        name="Nibblefox", personality="picnic-loving fox, cheeks always full of snacks",
        body=(244, 154, 80), belly=(255, 246, 236), accent=(112, 70, 54), accent2=(222, 70, 82),
        eye=(80, 40, 36), blush_c=(255, 140, 120), eyes="happy", mouth="w", blush="puff",
        head=(0.37, 0.30, 0.32), parts=["face_mask", "fox_ears", "cheek_fluff", "striped_tail", "picnic_pouch"], pose="stand",
    ),
    "DewdropFawn": dict(
        name="Dewdrop Fawn", personality="sleepy fawn, wakes up covered in morning dew",
        body=(236, 214, 210), belly=(255, 248, 246), accent=(140, 200, 240), accent2=(214, 236, 252),
        eye=(90, 80, 124), blush_c=(170, 206, 250), eyes="sleepy", mouth="o", blush="drop",
        head=(0.37, 0.31, 0.33), parts=["muzzle", "fawn_ears", "dew_marks", "dewdrop"], pose="sit",
    ),
    "Tumblehog": dict(
        name="Tumblehog", personality="round hedgehog, rolls down hills like a flower bud",
        body=(216, 184, 156), belly=(255, 240, 226), accent=(250, 166, 188), accent2=(255, 206, 160),
        eye=(90, 56, 48), blush_c=(255, 150, 170), eyes="round", mouth="smile", blush="petal",
        head=(0.38, 0.31, 0.34), parts=["face_mask", "bear_ears_small", "petal_quills", "snout"], pose="sit",
    ),
    "MapleMip": dict(
        name="Maple Mip", personality="little raccoon hiker, collects maple leaves in its wooden backpack",
        body=(164, 160, 172), belly=(238, 234, 238), accent=(230, 96, 58), accent2=(176, 124, 82),
        eye=(56, 42, 58), blush_c=(255, 150, 120), eyes="round", mouth="w", blush="maple",
        head=(0.37, 0.31, 0.33), parts=["bear_ears_small", "raccoon_mask", "maple_mark", "ringed_tail", "wood_backpack"], pose="stand",
    ),
    "PuddlePaws": dict(
        name="Puddle Paws", personality="baby otter, jumps in every puddle and keeps the smoothest pebble",
        body=(150, 110, 86), belly=(236, 214, 190), accent=(255, 206, 70), accent2=(150, 172, 194),
        eye=(60, 40, 34), blush_c=(255, 160, 140), eyes="happy", mouth="w", blush="ripple",
        head=(0.37, 0.30, 0.33), parts=["bear_ears_small", "muzzle", "raincoat", "pebble", "otter_tail"], pose="sit",
        held=["pebble"],
    ),
    "Honeyhop": dict(
        name="Honeyhop", personality="golden field mouse, carries a honey jar almost as big as itself",
        body=(246, 206, 112), belly=(255, 244, 214), accent=(238, 158, 40), accent2=(255, 180, 192),
        eye=(100, 60, 30), blush_c=(255, 150, 110), eyes="round", mouth="open", blush="hex",
        head=(0.37, 0.31, 0.33), parts=["face_mask", "mouse_ears", "thin_tail", "honey_jar"], pose="stand",
        held=["honey_jar"],
    ),
    "AcornOwl": dict(
        name="Acorn Owl", personality="tiny night owl, raises its leafy eyebrows at everything",
        body=(132, 96, 76), belly=(246, 228, 200), accent=(116, 174, 88), accent2=(255, 196, 72),
        eye=(56, 36, 28), blush_c=(250, 160, 140), eyes="round", mouth="none", blush="feather",
        head=(0.38, 0.33, 0.34), parts=["owl_face", "leaf_brows", "leaf_tufts", "beak", "wings", "branch_perch"], pose="stand",
        arms=False, feet="beakc", held=["branch_perch"],
    ),
    "Thimbletail": dict(
        name="Thimbletail", personality="sleepy dormouse, wears a thimble as a hat and its tail as a blanket",
        body=(204, 186, 210), belly=(250, 242, 250), accent=(214, 216, 226), accent2=(255, 184, 204),
        eye=(70, 56, 92), blush_c=(250, 170, 204), eyes="sleepy", mouth="w", blush="button",
        head=(0.38, 0.32, 0.33), parts=["face_mask", "mouse_ears_small", "curl_tail", "thimble_hat"], pose="sit",
    ),
    "PetalPika": dict(
        name="Petal Pika", personality="mountain pika in tiny climbing boots, picks a flower at every summit",
        body=(222, 190, 160), belly=(252, 240, 226), accent=(246, 128, 170), accent2=(190, 88, 62),
        eye=(80, 50, 50), blush_c=(255, 140, 180), eyes="happy", mouth="smile", blush="flower",
        head=(0.38, 0.32, 0.33), parts=["face_mask", "pika_ears", "flower_tuft", "boots"], pose="stand",
        feet="accent2",
    ),
    "WaffleWeasel": dict(
        name="Waffle Weasel", personality="mischievous weasel, swaps everyone's breakfast when they look away",
        body=(230, 196, 140), belly=(255, 248, 232), accent=(212, 142, 62), accent2=(120, 80, 50),
        eye=(70, 44, 32), blush_c=(255, 160, 130), eyes="smug", mouth="smirk", blush="grid",
        head=(0.36, 0.29, 0.32), parts=["face_mask", "bear_ears_small", "waffle_scarf", "curl_tail_small"], pose="stand",
    ),
    "DandelionDot": dict(
        name="Dandelion Dot", personality="baby bunny with a dandelion tail, makes a wish with every hop",
        body=(255, 248, 230), belly=(255, 255, 250), accent=(255, 208, 66), accent2=(255, 190, 200),
        eye=(110, 88, 50), blush_c=(255, 196, 110), eyes="round", mouth="o", blush="seed",
        head=(0.37, 0.32, 0.33), parts=["short_bunny_ears", "dandelion_tail", "seed_floaters"], pose="stand",
    ),
    "WillowWren": dict(
        name="Willow Wren", personality="round little songbird, plays a twig flute at sunrise",
        body=(190, 146, 106), belly=(250, 236, 216), accent=(126, 178, 98), accent2=(250, 186, 86),
        eye=(60, 40, 30), blush_c=(255, 170, 150), eyes="sparkle", mouth="none", blush="note",
        head=(0.36, 0.32, 0.34), parts=["beak", "leaf_wings", "wren_tail", "twig_flute"], pose="stand",
        arms=False, feet="beakc", held=["twig_flute"],
    ),
}
ORDER = list(CAST.keys())


# =========================================================================== atlas swatches
def swatches(c, swatch, grain=0.0):
    """Extra regions every character atlas gets (used by these parts and the props)."""
    out = {
        "leafgreen": swatch((112, 176, 90), grain=grain),
        "bamboo": swatch((214, 196, 110)),
        "clay": swatch((196, 104, 70)),
        "water": swatch((130, 196, 240)),
        "glassy": swatch((222, 240, 252)),
        "beakc": swatch((250, 186, 80)),
        "raincoat": swatch((255, 206, 70), grain=grain),
        "pebble": swatch((150, 168, 186)),
        "honey": _honey(),
        "gingham": _gingham((222, 70, 82)),
        "waffle": _waffle(c["accent"]),
        "thimble": _thimble(),
        "acorncap": _acorncap(c["accent"]),
        "leafwing": _leafwing(c["accent"], c["body"]),
        "petal1": swatch((250, 166, 188), grain=grain),
        "petal2": swatch((255, 206, 160), grain=grain),
        "kite": _kite(),
        "drumtop": swatch((248, 246, 240), grad=False),
        "dark2": swatch(tuple(int(v * 0.58) for v in c["body"]), grain=grain),
    }
    return out


def _gingham(col, size=64):
    im = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    light = tuple(int(v * 0.5 + 255 * 0.5) for v in col)
    for i in range(0, size, 16):
        d.rectangle([i, 0, i + 7, size], fill=light + (255,))
        d.rectangle([0, i, size, i + 7], fill=light + (255,))
    for i in range(0, size, 16):
        for j in range(0, size, 16):
            d.rectangle([i, j, i + 7, j + 7], fill=col + (255,))
    return im


def _waffle(col, size=64):
    im = Image.new("RGBA", (size, size), col + (255,))
    d = ImageDraw.Draw(im)
    dark = tuple(int(v * 0.72) for v in col)
    for i in range(0, size, 12):
        d.line([(i, 0), (i, size)], fill=dark + (255,), width=3)
        d.line([(0, i), (size, i)], fill=dark + (255,), width=3)
    return im


def _thimble(size=64):
    im = Image.new("RGBA", (size, size), (212, 216, 226, 255))
    d = ImageDraw.Draw(im)
    for j in range(0, size, 8):
        for i in range(0, size, 8):
            x = i + (4 if (j // 8) % 2 else 0)
            d.ellipse([x + 2, j + 2, x + 5, j + 5], fill=(168, 172, 186, 255))
    return im


def _acorncap(col, size=64):
    im = Image.new("RGBA", (size, size), col + (255,))
    d = ImageDraw.Draw(im)
    dark = tuple(int(v * 0.75) for v in col)
    for j in range(0, size + 8, 8):
        for i in range(0, size + 8, 10):
            x = i + (5 if (j // 8) % 2 else 0)
            d.arc([x - 6, j - 4, x + 6, j + 6], 0, 180, fill=dark + (255,), width=2)
    return im


def _leafwing(col, base, size=64):
    """Body colour with two thin leaf veins: the wing feathers look like leaves."""
    im = Image.new("RGBA", (size, size), base + (255,))
    d = ImageDraw.Draw(im)
    light = tuple(int(v * 0.6 + w * 0.4) for v, w in zip(col, base))
    for y in (20, 44):
        d.ellipse([10, y - 6, 54, y + 6], fill=light + (255,))
        d.line([(12, y), (52, y)], fill=tuple(int(v * 0.75) for v in col) + (255,), width=2)
    return im


def _honey(size=64):
    im = Image.new("RGBA", (size, size), (236, 160, 40, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 22, size, 44], fill=(255, 246, 220, 255))           # label band
    for k in range(4):                                                    # little hexagons on the label
        cx, cy, r = 10 + k * 15, 33, 5
        d.polygon([(cx + r * math.cos(a), cy + r * math.sin(a)) for a in [i * math.pi / 3 for i in range(6)]], fill=(246, 190, 70, 255))
    d.line([(10, 2), (10, 20)], fill=(255, 220, 140, 255), width=4)     # shine
    return im


def _kite(size=64):
    im = Image.new("RGBA", (size, size), (255, 210, 70, 255))
    d = ImageDraw.Draw(im)
    d.polygon([(0, 0), (size, 0), (size // 2, size // 2)], fill=(240, 90, 110, 255))
    d.polygon([(0, size), (size, size), (size // 2, size // 2)], fill=(90, 170, 230, 255))
    d.polygon([(0, 0), (0, size), (size // 2, size // 2)], fill=(120, 196, 110, 255))
    return im


# =========================================================================== painting
def paint_head_extra(p, c):
    P = c["parts"]
    if "raccoon_mask" in P:
        mask = (98, 92, 104, 255)
        for side in (-1, 1):
            p.ellipse(side * 0.36, -0.08, 0.30, 0.25, mask)
        p.ellipse(0, -0.02, 0.16, 0.12, mask)
        for side in (-1, 1):
            p.ellipse(side * 0.37, -0.10, 0.17, 0.22, (255, 255, 255, 255))
        p.ellipse(0, 0.30, 0.10, 0.18, c["belly"] + (255,))   # light stripe up the forehead
    if "owl_face" in P:
        for side in (-1, 1):
            p.ellipse(side * 0.37, -0.10, 0.27, 0.30, c["belly"] + (255,))
    if "deer_spots" in P:
        rng = np.random.default_rng(21)
        for _ in range(22):
            lon = rng.uniform(-math.pi, math.pi)
            if abs(lon) < 1.3:
                continue
            p.ellipse(lon, rng.uniform(-0.3, 1.0), 0.05, 0.055, c["belly"] + (255,))
    if "dew_marks" in P:
        for lon, lat in ((2.1, 0.5), (-2.3, 0.3), (2.8, -0.1), (-2.8, 0.7), (1.6, 0.9), (-1.6, 0.85)):
            _drop(p, lon, lat, 0.06, c["accent"] + (255,))
    if "maple_mark" in P:
        _maple(p, 0.0, 0.66, 0.10, c["accent"] + (255,))


def paint_body_extra(p, c):
    P = c["parts"]
    if "deer_spots" in P:
        rng = np.random.default_rng(22)
        for _ in range(16):
            lon = rng.uniform(-math.pi, math.pi)
            if abs(lon) < 1.2:
                continue
            p.ellipse(lon, rng.uniform(-0.4, 0.9), 0.07, 0.08, c["belly"] + (255,))
    if "dew_marks" in P:
        for lon, lat in ((2.2, 0.3), (-2.4, 0.1), (3.0, 0.5), (-2.9, -0.2)):
            _drop(p, lon, lat, 0.09, c["accent"] + (255,))
    if "maple_mark" in P:
        _maple(p, 0.0, 0.0, 0.26, c["accent"] + (255,))
    if "honey_tummy" in P:
        pass


def _drop(p, lon, lat, r, col):
    p.ellipse(lon, lat - r * 0.3, r * 0.7, r * 0.7, col)
    p.poly([(lon - r * 0.62, lat - r * 0.05), (lon + r * 0.62, lat - r * 0.05), (lon, lat + r)], col)


def _maple(p, lon, lat, r, col):
    p.star(lon, lat, r, col, points=5, inner=0.5)
    for k in (-1, 1):
        p.star(lon + k * r * 0.55, lat + r * 0.05, r * 0.55, col, points=3, inner=0.5)
    p.line([(lon, lat - r * 0.3), (lon, lat - r * 1.1)], col, r * 0.12)


def blush(p, b, x, by, side, bl):
    """The new signature cheek shapes. Returns False if it isn't one of ours."""
    if b == "acorn":
        p.ellipse(x, by - 0.01, 0.06, 0.07, bl)
        p.ellipse(x, by + 0.05, 0.075, 0.035, shade_a(bl, 0.75))
    elif b == "freckle":
        for dx, dy in ((-0.05, 0.02), (0.05, 0.02), (0.0, -0.04)):
            p.ellipse(x + dx, by + dy, 0.025, 0.025, bl)
    elif b == "tulip":
        p.ellipse(x, by - 0.02, 0.06, 0.05, bl)
        for dx in (-0.045, 0.0, 0.045):
            p.poly([(x + dx - 0.025, by), (x + dx + 0.025, by), (x + dx, by + 0.06)], bl)
    elif b == "clover":
        for a in (90, 210, 330):
            r = math.radians(a)
            p.ellipse(x + 0.04 * math.cos(r), by + 0.04 * math.sin(r), 0.035, 0.035, bl)
    elif b == "puff":
        p.ellipse(x, by, 0.13, 0.08, bl)
        p.ellipse(x - side * 0.03, by + 0.02, 0.03, 0.02, (255, 255, 255, 200))
    elif b == "drop":
        _drop(p, x, by, 0.07, bl)
    elif b == "petal":
        for a in (-30, 30):
            r = math.radians(a)
            p.ellipse(x + 0.035 * math.sin(r), by + 0.02, 0.03, 0.06, bl)
    elif b == "maple":
        _maple(p, x, by, 0.06, bl)
    elif b == "ripple":
        p.ellipse(x, by, 0.025, 0.02, bl)
        p.arc(x, by, 0.07, 0.045, 0, 360, bl, 0.014)
        p.arc(x, by, 0.11, 0.07, 200, 340, bl, 0.012)
    elif b == "hex":
        r = 0.065
        p.poly([(x + r * math.cos(a), by + r * math.sin(a)) for a in [i * math.pi / 3 for i in range(6)]], bl)
    elif b == "feather":
        p.poly([(x - 0.08, by - 0.03), (x - 0.02, by + 0.03), (x + 0.08, by + 0.04), (x + 0.02, by - 0.03)], bl)
        p.line([(x - 0.08, by - 0.03), (x + 0.08, by + 0.04)], shade_a(bl, 0.75), 0.008)
    elif b == "button":
        p.ellipse(x, by, 0.065, 0.065, bl)
        for dx in (-0.018, 0.018):
            for dy in (-0.018, 0.018):
                p.ellipse(x + dx, by + dy, 0.009, 0.009, (255, 255, 255, 230))
    elif b == "flower":
        for k in range(5):
            a = TAU * k / 5 + math.pi / 2
            p.ellipse(x + 0.04 * math.cos(a), by + 0.04 * math.sin(a), 0.03, 0.03, bl)
        p.ellipse(x, by, 0.02, 0.02, (255, 236, 150, 255))
    elif b == "grid":
        p.ellipse(x, by, 0.07, 0.06, bl)
        for k in (-1, 0, 1):
            p.line([(x + k * 0.03, by - 0.05), (x + k * 0.03, by + 0.05)], shade_a(bl, 0.75), 0.008)
            p.line([(x - 0.06, by + k * 0.025), (x + 0.06, by + k * 0.025)], shade_a(bl, 0.75), 0.008)
    elif b == "seed":
        for k in range(6):
            a = TAU * k / 6
            p.line([(x, by), (x + 0.07 * math.cos(a), by + 0.07 * math.sin(a))], bl, 0.012)
        p.ellipse(x, by, 0.02, 0.02, bl)
    elif b == "note":
        p.ellipse(x - 0.02, by - 0.04, 0.035, 0.028, bl)
        p.line([(x + 0.012, by - 0.04), (x + 0.012, by + 0.07)], bl, 0.014)
        p.line([(x + 0.012, by + 0.07), (x + 0.06, by + 0.04)], bl, 0.014)
    else:
        return False
    return True


def shade_a(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c[:3]) + (c[3],)


# =========================================================================== parts
def _chain(B, pts, radii, regions, step=0.03, s=1.0, nu=10, nv=7):
    """Soft ellipsoids along a polyline (tails). radii/regions: one per point, interpolated / cycled per bead."""
    pts = [np.array(p, dtype=float) for p in pts]
    beads = []
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        n = max(1, int(np.linalg.norm(b - a) / step))
        for k in range(n):
            t = k / n
            beads.append((a + (b - a) * t, radii[i] + (radii[i + 1] - radii[i]) * t))
    beads.append((pts[-1], radii[-1]))
    for j, (p, r) in enumerate(beads):
        reg = regions[j % len(regions)] if callable(regions) is False else regions(j, len(beads))
        B.ellipsoid(tuple(p * s), (r * s, r * s, r * s), reg, nu=nu, nv=nv)


def _flower(B, centre, r, petal, middle="yellow", normal=(0, 0, 1), n=5):
    """A flat little flower facing `normal`."""
    R = align_y(normal)
    c = np.asarray(centre, dtype=float)
    # two directions in the flower's plane
    u = R @ np.array([1.0, 0, 0])
    w = R @ np.array([0, 0, 1.0])
    for k in range(n):
        a = TAU * k / n
        d = u * math.cos(a) + w * math.sin(a)
        B.ellipsoid(tuple(c + d * r * 0.9), (r * 0.6, r * 0.25, r * 0.6), petal, rot=R, nu=8, nv=4)
    B.ellipsoid(tuple(c + R @ np.array([0, r * 0.12, 0])), (r * 0.45, r * 0.3, r * 0.45), middle, rot=R, nu=8, nv=5)


def _head_point(c, head_y, lon, lat, out=0.0):
    hx, hy, hz = c["head"]
    return np.array([(hx + out) * math.cos(lat) * math.sin(lon), head_y + (hy + out) * math.sin(lat),
                     0.01 + (hz + out) * math.cos(lat) * math.cos(lon)])


def _head_normal(c, lon, lat):
    hx, hy, hz = c["head"]
    n = np.array([math.cos(lat) * math.sin(lon) / hx, math.sin(lat) / hy, math.cos(lat) * math.cos(lon) / hz])
    return n / np.linalg.norm(n)


def _spiral_tail(B, s, start, cy, cz, r0, turns, bead, region, shrink=0.6, n=34):
    pts = [np.array(start)]
    for i in range(n + 1):
        t = i / n
        th = turns * TAU * t
        r = r0 * (1 - shrink * t)
        pts.append(np.array([0.0, cy - r * math.cos(th), cz - r * math.sin(th)]))
    for i, p in enumerate(pts):
        rr = bead * (1 - 0.45 * i / len(pts))
        B.ellipsoid(tuple(p * s), (rr * s, rr * s, rr * s), region, nu=10, nv=6)


# parts that stick out of the back: left off a worn mascot bag (its back rests on the wearer)
BACK_PARTS = {"bushy_tail", "striped_tail", "ringed_tail", "wood_backpack", "otter_tail", "thin_tail", "curl_tail", "curl_tail_small",
              "dandelion_tail", "seed_floaters", "wren_tail", "puff_tail"}


def build_parts(B, key, c, s, by, head_y, top, sit, plush, props=True, bag=False):
    """Adds this character's silhouette parts (called at the end of kawaii.build_character)."""
    P = [p for p in c["parts"] if (props or p not in c.get("held", [])) and not (bag and p in BACK_PARTS)]
    m = B.m
    A = B.A

    if "squirrel_ears" in P:
        for side in (-1, 1):
            B.lathe([(0.0, 0), (0.07, 0.0), (0.045, 0.09), (0.0, 0.16)], "main", base=(side * 0.27 * s, (top - 0.02) * s, -0.04 * s),
                    rot=rot_xyz(rz=-side * 28), nu=10, squash=(1.0, 0.55), scale=s)
            B.ellipsoid((side * 0.35 * s, (top + 0.12) * s, -0.04 * s), (0.03 * s, 0.05 * s, 0.03 * s), "accent", nu=8, nv=6)
    if "acorn_cap" in P:
        B.lathe([(0.0, 0.0), (0.40, 0.0), (0.42, 0.045), (0.385, 0.12), (0.29, 0.20), (0.15, 0.255), (0.0, 0.27)], "acorncap",
                base=(0, (head_y + 0.12) * s, -0.01 * s), rot=rot_xyz(rz=-7), nu=30, scale=s)
        B.lathe([(0.0, 0), (0.035, 0.0), (0.028, 0.08), (0.0, 0.09)], "darkwood", base=(0.035 * s, (head_y + 0.38) * s, -0.01 * s),
                rot=rot_xyz(rz=-25), nu=8, scale=s)
    if "bushy_tail" in P:
        _chain(B, [(0, by - 0.06, -0.20), (0, by + 0.04, -0.36), (0, by + 0.24, -0.44), (0, by + 0.46, -0.42), (0, by + 0.62, -0.32),
                   (0, by + 0.70, -0.20)], [0.10, 0.13, 0.15, 0.15, 0.13, 0.10], ["main"], step=0.035, s=s)
        B.ellipsoid((0, (by + 0.70) * s, -0.16 * s), (0.09 * s, 0.08 * s, 0.08 * s), "belly", nu=12, nv=8)
    if "held_nut" in P:
        z = 0.25
        B.ellipsoid((0, (by + 0.02) * s, z * s), (0.075 * s, 0.09 * s, 0.07 * s), "accent2", nu=16, nv=10)
        B.lathe([(0.0, 0.0), (0.085, 0.0), (0.08, 0.035), (0.0, 0.06)], "acorncap", base=(0, (by + 0.07) * s, z * s), nu=16, scale=s)
        B.lathe([(0.0, 0), (0.012, 0.0), (0.0, 0.04)], "darkwood", base=(0, (by + 0.125) * s, z * s), nu=6, scale=s)

    if "deer_ears" in P or "fawn_ears" in P:
        droop = 10 if "deer_ears" in P else -14
        for side in (-1, 1):
            cpos = _head_point(c, head_y, side * 1.45, 0.42)
            B.ellipsoid(tuple(cpos * s + np.array([side * 0.07 * s, 0, 0])), (0.15 * s, 0.07 * s, 0.05 * s), "main",
                        rot=rot_xyz(rz=side * droop, ry=-side * 10), nu=14, nv=8)
            B.ellipsoid(tuple(cpos * s + np.array([side * 0.08 * s, 0, 0.03 * s])), (0.10 * s, 0.045 * s, 0.02 * s), "pinkprop",
                        rot=rot_xyz(rz=side * droop, ry=-side * 10), nu=12, nv=6)
            if "fawn_ears" in P:  # dewy translucent tips
                tip = cpos + np.array([side * 0.20, math.sin(math.radians(droop)) * side * 0.20 * 0 - 0.03, 0])
                B.ellipsoid(tuple(tip * s), (0.06 * s, 0.05 * s, 0.045 * s), "glassy", nu=10, nv=6)
    if "fern_antlers" in P:
        for side in (-1, 1):
            base = np.array([side * 0.12, top - 0.03, -0.02])
            tipp = np.array([side * 0.26, top + 0.24, -0.04])
            m.bar(tuple(base * s), tuple(tipp * s), 0.028 * s, 0.028 * s, A.uv("accent"))
            for k in range(4):
                t = 0.3 + 0.2 * k
                p = base + (tipp - base) * t
                for lr in (-1, 1):
                    B.ellipsoid(tuple((p + np.array([lr * 0.045, 0.01, 0])) * s), (0.045 * s, 0.018 * s, 0.022 * s), "leafgreen",
                                rot=rot_xyz(rz=-lr * 25), nu=8, nv=5)
            B.ellipsoid(tuple((tipp + np.array([0, 0.02, 0])) * s), (0.03 * s, 0.045 * s, 0.022 * s), "leafgreen", nu=8, nv=5)
    if "ear_flower" in P:
        p = _head_point(c, head_y, 1.15, 0.55, out=0.02)
        _flower(B, p * s, 0.06 * s, "accent2", normal=_head_normal(c, 1.15, 0.55))

    if "tulip_ears" in P:
        for side in (-1, 1):
            b = (side * 0.13 * s, (top - 0.06) * s, -0.02 * s)
            R = rot_xyz(rz=-side * 12)
            B.lathe([(0.0, 0.0), (0.06, 0.03), (0.10, 0.13), (0.105, 0.26), (0.08, 0.35), (0.0, 0.33)], "accent", base=b, rot=R,
                    nu=16, squash=(1.0, 0.75), scale=s)
            for k in range(3):  # tulip petal tips
                a = TAU * k / 3
                off = R @ np.array([0.065 * math.sin(a), 0.34, 0.045 * math.cos(a)])
                B.lathe([(0.0, 0.0), (0.045, 0.0), (0.0, 0.10)], "accent", base=tuple(np.array(b) + off * s), rot=R, nu=8, scale=s)
            B.ellipsoid((side * 0.20 * s, (top - 0.02) * s, 0.02 * s), (0.06 * s, 0.02 * s, 0.03 * s), "accent2",
                        rot=rot_xyz(rz=-side * 30), nu=8, nv=5)
    if "flower_crown" in P:
        hx, hy, hz = c["head"]
        for k in range(10):
            a = TAU * k / 10
            lat = 0.62
            p = np.array([hx * math.cos(lat) * math.sin(a), head_y + hy * math.sin(lat), 0.01 + hz * math.cos(lat) * math.cos(a)])
            if k % 2 == 0:
                _flower(B, p * s, 0.05 * s, ["white", "yellow", "pinkprop"][(k // 2) % 3], normal=(math.sin(a) * 0.6, 0.8, math.cos(a) * 0.6))
            else:
                B.ellipsoid(tuple(p * s), (0.04 * s, 0.02 * s, 0.03 * s), "accent2", rot=rot_xyz(ry=math.degrees(a)), nu=8, nv=5)
    if "puff_tail" in P:
        B.ellipsoid((0, (by - 0.06) * s, -0.23 * s), (0.08 * s, 0.08 * s, 0.07 * s), "belly", nu=12, nv=8)

    if "clover_paws" in P:
        for side in (-1, 1):
            x = side * 0.12
            for k in range(3):
                a = TAU * k / 3 + math.pi / 2
                if sit:   # on the soles, facing forward
                    B.ellipsoid(((x + 0.025 * math.cos(a)) * s, (0.075 + 0.025 * math.sin(a)) * s, 0.285 * s), (0.022 * s, 0.022 * s, 0.006 * s),
                                "accent", nu=8, nv=4)
                else:     # on top of the feet
                    B.ellipsoid(((x + 0.025 * math.cos(a)) * s, 0.09 * s, (0.11 + 0.025 * math.sin(a)) * s), (0.022 * s, 0.006 * s, 0.022 * s),
                                "accent", nu=8, nv=4)
    if "lucky_charm" in P:
        B.lathe([(0.0, -0.01), (0.215, -0.01), (0.22, 0.0), (0.215, 0.01), (0.0, 0.01)], "gold", base=(0, (by + 0.19) * s, 0), nu=28, scale=s)
        cz = 0.205 if not sit else 0.215
        cy = by + 0.08
        for k in range(4):
            a = TAU * k / 4 + math.pi / 4
            B.ellipsoid(((0.03 * math.cos(a)) * s, (cy + 0.03 * math.sin(a)) * s, cz * s), (0.03 * s, 0.03 * s, 0.01 * s), "accent", nu=10, nv=5)
        B.ellipsoid((0, (cy + 0.075) * s, (cz - 0.01) * s), (0.015 * s, 0.015 * s, 0.01 * s), "gold", nu=8, nv=5)

    if "fox_ears" in P:
        for side in (-1, 1):
            R = rot_xyz(rz=-side * 18)
            b = (side * 0.21 * s, (top - 0.11) * s, -0.03 * s)
            B.lathe([(0.0, 0), (0.13, 0.0), (0.08, 0.12), (0.0, 0.23)], "main", base=b, rot=R, nu=12, squash=(1.0, 0.5), scale=s)
            B.lathe([(0.0, 0), (0.075, 0.0), (0.04, 0.09), (0.0, 0.15)], "belly", base=(b[0], b[1] + 0.01 * s, b[2] + 0.03 * s), rot=R,
                    nu=10, squash=(1.0, 0.3), scale=s)
            tip = np.array(b) + R @ np.array([0, 0.19 * s, 0])
            B.lathe([(0.0, 0), (0.045, 0.0), (0.0, 0.06)], "accent", base=tuple(tip), rot=R, nu=10, squash=(1.0, 0.5), scale=s)
    if "cheek_fluff" in P:
        for side in (-1, 1):
            B.ellipsoid((side * 0.33 * s, (head_y - 0.12) * s, 0.10 * s), (0.11 * s, 0.085 * s, 0.10 * s), "belly", nu=12, nv=8)
            B.ellipsoid((side * 0.42 * s, (head_y - 0.15) * s, 0.06 * s), (0.06 * s, 0.05 * s, 0.06 * s), "belly",
                        rot=rot_xyz(rz=side * 30), nu=10, nv=6)
    if "striped_tail" in P or "ringed_tail" in P:
        fox = "striped_tail" in P
        pts = [(0.0, by - 0.08, -0.20), (0.10, by - 0.02, -0.36), (0.20, by + 0.12, -0.44), (0.26, by + 0.32, -0.42), (0.24, by + 0.48, -0.34)]
        rad = [0.08, 0.11, 0.13, 0.12, 0.09] if fox else [0.07, 0.09, 0.10, 0.095, 0.08]
        regs = (lambda j, n: "belly" if j >= n - 3 else ("main" if (j // 3) % 2 == 0 else "accent")) if fox else \
            (lambda j, n: "main" if (j // 2) % 2 == 0 else "dark2")
        _chain(B, pts, rad, regs, step=0.03, s=s)
    if "picnic_pouch" in P:
        m.box(0.17 * s, 0.33 * s, (by - 0.12) * s, (by + 0.02) * s, 0.08 * s, 0.18 * s, A.uv("gingham"), top=A.uv("gingham"))
        m.bar((0.12 * s, (by + 0.2) * s, 0.10 * s), (0.25 * s, (by + 0.02) * s, 0.16 * s), 0.025 * s, 0.012 * s, A.uv("darkwood"))

    if "dewdrop" in P:
        B.lathe([(0.0, 0.0), (0.05, 0.015), (0.06, 0.045), (0.04, 0.08), (0.0, 0.13)], "glassy",
                base=(0.08 * s, (top - 0.025) * s, 0.04 * s), rot=rot_xyz(rz=-15), nu=14, scale=s)

    if "petal_quills" in P:
        rng = np.random.default_rng(31)
        hx, hy, hz = c["head"]
        k = 0
        for lat in np.linspace(-0.25, 1.25, 7):
            n_ring = max(3, int(16 * math.cos(lat) + 2))
            for i in range(n_ring):
                lon = math.pi + (i / n_ring - 0.5) * 2 * (math.pi - 1.05) + rng.uniform(-0.08, 0.08)
                lon = (lon + math.pi) % TAU - math.pi
                if abs(lon) < 1.05 and lat < 1.0:
                    continue
                p = _head_point(c, head_y, lon, lat, out=-0.01)
                nrm = _head_normal(c, lon, lat)
                d = nrm + np.array([0, 0.2, -0.35])
                R = align_y(d)
                B.ellipsoid(tuple((p + R @ np.array([0, 0.05, 0])) * s), (0.055 * s, 0.09 * s, 0.03 * s), "petal1" if k % 2 else "petal2",
                            rot=R, nu=7, nv=4)
                k += 1
        for lat in np.linspace(-0.6, 0.9, 5):  # down the back of the body
            for lon in np.linspace(2.0, TAU - 2.0, 6):
                lon2 = (lon + math.pi) % TAU - math.pi
                cx, cy2, cz = 0.0, by, 0.0
                rr = np.array([0.25 * math.cos(lat) * math.sin(lon2), 0.24 * math.sin(lat), 0.22 * math.cos(lat) * math.cos(lon2)])
                nrm = rr / np.linalg.norm(rr)
                R = align_y(nrm + np.array([0, 0.3, -0.3]))
                p = np.array([cx, cy2, cz]) + rr + R @ np.array([0, 0.04, 0])
                B.ellipsoid(tuple(p * s), (0.055 * s, 0.085 * s, 0.03 * s), "petal1" if k % 2 else "petal2", rot=R, nu=7, nv=4)
                k += 1
    if "snout" in P:
        B.ellipsoid((0, (head_y - 0.16) * s, (c["head"][2] - 0.02) * s), (0.10 * s, 0.07 * s, 0.08 * s), "belly", nu=12, nv=8)
        B.ellipsoid((0, (head_y - 0.15) * s, (c["head"][2] + 0.06) * s), (0.035 * s, 0.028 * s, 0.025 * s), "black", nu=8, nv=6)

    if "wood_backpack" in P:
        m.box(-0.14 * s, 0.14 * s, (by - 0.06) * s, (by + 0.22) * s, -0.36 * s, -0.20 * s, A.uv("wood"), top=A.uv("darkwood"))
        m.box(-0.10 * s, 0.10 * s, (by + 0.10) * s, (by + 0.24) * s, -0.375 * s, -0.355 * s, A.uv("darkwood"))
        B.ellipsoid((0.0, (by + 0.04) * s, -0.37 * s), (0.05 * s, 0.05 * s, 0.012 * s), "accent", nu=10, nv=5)  # a maple-red badge
        for side in (-1, 1):
            m.bar((side * 0.12 * s, (by + 0.21) * s, 0.06 * s), (side * 0.12 * s, (by - 0.02) * s, 0.20 * s), 0.03 * s, 0.014 * s, A.uv("darkwood"))

    if "raincoat" in P:
        k = 1.07
        B.ellipsoid((0, by * s, 0), (0.25 * s * k, 0.245 * s * k, 0.22 * s * k), "raincoat", nu=24, nv=12)
        for side in (-1, 1):
            B.ellipsoid((side * 0.25 * s, (by + 0.05) * s, 0.04 * s), (0.085 * s, 0.10 * s, 0.085 * s), "raincoat",
                        rot=rot_xyz(rz=side * 35, rx=-15), nu=12, nv=8)
        B.ellipsoid((0, (head_y - 0.17) * s, -0.17 * s), (0.25 * s, 0.11 * s, 0.13 * s), "raincoat", nu=18, nv=10)  # hood, down
        for k2 in range(3):
            yy = by + 0.14 - k2 * 0.09
            zz = 0.236 * math.sqrt(max(0.05, 1 - ((yy - by) / 0.26) ** 2))
            B.ellipsoid((0, yy * s, (zz + 0.005) * s), (0.022 * s, 0.022 * s, 0.01 * s), "white", nu=8, nv=5)
    if "pebble" in P:
        B.ellipsoid((0, (by + 0.04) * s, 0.27 * s), (0.09 * s, 0.055 * s, 0.07 * s), "pebble", rot=rot_xyz(rz=10), nu=14, nv=8)
    if "otter_tail" in P:
        B.ellipsoid((0.10 * s, 0.05 * s, -0.30 * s), (0.08 * s, 0.045 * s, 0.20 * s), "main", rot=rot_xyz(ry=-30), nu=14, nv=8)

    if "mouse_ears" in P or "mouse_ears_small" in P:
        r = 0.15 if "mouse_ears" in P else 0.10
        for side in (-1, 1):
            R = rot_xyz(rz=-side * 22)
            B.ellipsoid((side * 0.25 * s, (top - 0.02) * s, -0.04 * s), (r * s, r * s, 0.04 * s), "main", rot=R, nu=16, nv=8)
            B.ellipsoid((side * 0.25 * s, (top - 0.02) * s, -0.012 * s), (r * 0.68 * s, r * 0.68 * s, 0.02 * s), "accent2" if "mouse_ears" in P else "pinkprop",
                        rot=R, nu=14, nv=6)
    if "thin_tail" in P:
        pts = [(0.0, by - 0.10, -0.18), (0.08, by - 0.16, -0.34), (0.20, by - 0.12, -0.42), (0.28, by + 0.02, -0.40), (0.26, by + 0.12, -0.32)]
        _chain(B, pts, [0.03, 0.028, 0.025, 0.022, 0.02], ["pinkprop"], step=0.02, s=s, nu=8, nv=6)
    if "honey_jar" in P:
        z = 0.27
        B.lathe([(0.0, 0.0), (0.14, 0.0), (0.16, 0.04), (0.16, 0.19), (0.125, 0.245), (0.115, 0.26), (0.0, 0.26)], "honey",
                base=(0, 0.0, z * s), nu=24, scale=s)
        B.lathe([(0.0, 0.0), (0.135, 0.0), (0.15, 0.02), (0.12, 0.05), (0.0, 0.055)], "gingham", base=(0, 0.255 * s, z * s), nu=20, scale=s)
        B.lathe([(0.0, -0.01), (0.122, -0.01), (0.127, 0.0), (0.122, 0.01), (0.0, 0.01)], "rope", base=(0, 0.262 * s, z * s), nu=20, scale=s)

    if "owl_face" in P:
        pass
    if "leaf_brows" in P:
        for side in (-1, 1):
            p = _head_point(c, head_y, side * 0.40, 0.17, out=0.01)
            B.ellipsoid(tuple(p * s), (0.10 * s, 0.03 * s, 0.03 * s), "accent", rot=rot_xyz(rz=-side * 18, ry=side * 22), nu=10, nv=6)
    if "leaf_tufts" in P:
        for side in (-1, 1):
            B.ellipsoid((side * 0.25 * s, (top - 0.0) * s, -0.02 * s), (0.05 * s, 0.13 * s, 0.025 * s), "accent",
                        rot=rot_xyz(rz=-side * 30), nu=10, nv=6)
    if "beak" in P:
        p = _head_point(c, head_y, 0.0, -0.26, out=-0.02)
        B.lathe([(0.0, 0.0), (0.055, 0.0), (0.03, 0.05), (0.0, 0.085)], "beakc", base=tuple(p * s), rot=align_y((0, -0.35, 1)), nu=12,
                squash=(1.0, 0.8), scale=s)
    if "wings" in P or "leaf_wings" in P:
        reg = "dark" if "wings" in P else "leafwing"
        for side in (-1, 1):
            B.ellipsoid((side * 0.25 * s, (by + 0.03) * s, -0.06 * s), (0.06 * s, 0.18 * s, 0.14 * s), reg,
                        rot=rot_xyz(rz=side * 14, rx=12), nu=14, nv=10)
    if "branch_perch" in P:
        m.bar((-0.34 * s, 0.03 * s, 0.17 * s), (0.34 * s, 0.03 * s, 0.17 * s), 0.06 * s, 0.05 * s, A.uv("darkwood"))
        m.bar((0.20 * s, 0.03 * s, 0.17 * s), (0.30 * s, 0.10 * s, 0.24 * s), 0.025 * s, 0.025 * s, A.uv("darkwood"))
        B.ellipsoid((0.33 * s, 0.13 * s, 0.26 * s), (0.05 * s, 0.02 * s, 0.03 * s), "leafgreen", rot=rot_xyz(rz=30), nu=8, nv=5)

    if "curl_tail" in P:
        _spiral_tail(B, s, (0, by - 0.08, -0.22), cy=by + 0.30, cz=-0.40, r0=0.32, turns=0.95, bead=0.095, region="main")
    if "curl_tail_small" in P:
        _spiral_tail(B, s, (0, by - 0.06, -0.20), cy=by + 0.12, cz=-0.34, r0=0.16, turns=0.85, bead=0.06, region="main", n=20)
    if "thimble_hat" in P:
        B.lathe([(0.0, 0.0), (0.135, 0.0), (0.14, 0.025), (0.125, 0.15), (0.095, 0.195), (0.0, 0.205)], "thimble",
                base=(0.05 * s, (top - 0.06) * s, 0.0), rot=rot_xyz(rz=-14), nu=22, scale=s)

    if "pika_ears" in P:
        for side in (-1, 1):
            B.ellipsoid((side * 0.24 * s, (top - 0.04) * s, -0.02 * s), (0.10 * s, 0.09 * s, 0.05 * s), "main", nu=14, nv=8)
            B.ellipsoid((side * 0.24 * s, (top - 0.04) * s, 0.02 * s), (0.065 * s, 0.055 * s, 0.02 * s), "belly", nu=12, nv=6)
    if "flower_tuft" in P:
        B.lathe([(0.0, 0), (0.015, 0.0), (0.012, 0.10), (0.0, 0.11)], "leafgreen", base=(0.04 * s, (top - 0.02) * s, 0), rot=rot_xyz(rz=-15), nu=8, scale=s)
        _flower(B, (0.075 * s, (top + 0.09) * s, 0.0), 0.06 * s, "accent", normal=(0.2, 0.5, 1.0))
    if "boots" in P and not sit:
        for side in (-1, 1):
            B.lathe([(0.0, 0.0), (0.085, 0.0), (0.085, 0.10), (0.075, 0.13), (0.0, 0.13)], "accent2", base=(side * 0.11 * s, 0.0, 0.0), nu=14, scale=s)
            B.lathe([(0.0, -0.01), (0.087, -0.01), (0.09, 0.0), (0.087, 0.01), (0.0, 0.01)], "white", base=(side * 0.11 * s, 0.12 * s, 0.0), nu=14, scale=s)
            m.box((side * 0.11 - 0.09) * s, (side * 0.11 + 0.09) * s, 0.0, 0.02 * s, -0.10 * s, 0.17 * s, A.uv("darkwood"))

    if "waffle_scarf" in P:
        B.lathe([(0.0, -0.02), (0.25, -0.02), (0.275, 0.03), (0.25, 0.08), (0.0, 0.08)], "waffle", base=(0, (by + 0.15) * s, 0), nu=28, scale=s)
        B.ellipsoid((-0.14 * s, (by + 0.04) * s, 0.21 * s), (0.06 * s, 0.12 * s, 0.025 * s), "waffle", rot=rot_xyz(rz=-14), nu=10, nv=8)

    if "short_bunny_ears" in P:
        for side in (-1, 1):
            R = rot_xyz(rz=-side * 14)
            B.ellipsoid((side * 0.15 * s, (top + 0.06) * s, -0.02 * s), (0.075 * s, 0.17 * s, 0.05 * s), "main", rot=R, nu=14, nv=10)
            B.ellipsoid((side * 0.15 * s, (top + 0.05) * s, 0.02 * s), (0.045 * s, 0.12 * s, 0.02 * s), "accent2", rot=R, nu=12, nv=6)
            tip = np.array([side * 0.15, top + 0.20, -0.02]) + R @ np.array([0, 0.0, 0]) - np.array([0, 0, 0])
            B.ellipsoid(tuple(np.array([side * (0.15 + 0.035), top + 0.19, -0.02]) * s), (0.05 * s, 0.045 * s, 0.045 * s), "accent", nu=10, nv=6)
    if "dandelion_tail" in P:
        cen = np.array([0.0, by - 0.02, -0.30])
        B.ellipsoid(tuple(cen * s), (0.12 * s, 0.12 * s, 0.12 * s), "cream", nu=16, nv=10)
        n = 40
        for i in range(n):  # fibonacci sphere: seed spokes, only the ones pointing away from the body
            yv = 1 - 2 * (i + 0.5) / n
            r = math.sqrt(1 - yv * yv)
            th = i * 2.399963
            d = np.array([r * math.cos(th), yv, r * math.sin(th)])
            if d[2] > 0.35:
                continue
            a = cen + d * 0.10
            b = cen + d * 0.21
            m.bar(tuple(a * s), tuple(b * s), 0.008 * s, 0.008 * s, A.uv("white"))
            B.ellipsoid(tuple(b * s), (0.028 * s, 0.028 * s, 0.028 * s), "white", nu=8, nv=5)
    if "seed_floaters" in P:   # three seeds lifting off the dandelion tail
        cen = np.array([0.0, by - 0.02, -0.30])
        for d in ((0.55, 0.75, -0.35), (-0.6, 0.7, -0.4), (0.05, 0.95, -0.3)):
            d = np.array(d) / np.linalg.norm(d)
            p = cen + d * 0.36
            m.bar(tuple((cen + d * 0.10) * s), tuple(p * s), 0.007 * s, 0.007 * s, A.uv("white"))
            B.ellipsoid(tuple(p * s), (0.02 * s, 0.02 * s, 0.02 * s), "darkwood", nu=8, nv=5)
            for k in range(6):
                a = TAU * k / 6
                m.bar(tuple(p * s), tuple((p + np.array([0.055 * math.cos(a), 0.035, 0.055 * math.sin(a)])) * s), 0.006 * s, 0.006 * s, A.uv("white"))
    if "wren_tail" in P:
        for k, rz in enumerate((-16, 0, 16)):
            B.ellipsoid((rz * 0.004 * s, (by + 0.18) * s, -0.30 * s), (0.065 * s, 0.17 * s, 0.022 * s), "leafwing" if k == 1 else "dark",
                        rot=rot_xyz(rx=-38, rz=rz), nu=12, nv=8)
    if "twig_flute" in P:
        a = np.array([-0.22, by + 0.02, 0.24])
        b = np.array([0.26, by + 0.14, 0.26])
        m.bar(tuple(a * s), tuple(b * s), 0.035 * s, 0.035 * s, A.uv("darkwood"))
        for t in (0.55, 0.68, 0.81):
            p = a + (b - a) * t + np.array([0, 0.012, 0.016])
            B.ellipsoid(tuple(p * s), (0.008 * s, 0.008 * s, 0.004 * s), "black", nu=6, nv=4)
        B.ellipsoid(tuple((b + np.array([0.04, 0.03, 0])) * s), (0.05 * s, 0.018 * s, 0.03 * s), "leafgreen", rot=rot_xyz(rz=35), nu=8, nv=5)
    return B


# =========================================================================== Fiesta Series props
FIESTA_THEMES = {
    "Mani": "Mani Vendor",
    "Tinikling": "Tinikling Dancer",
    "Sampaguita": "Sampaguita Seller",
    "ColorGame": "Color Game Champ",
    "Fishball": "Fishball Suki",
    "Pandanggo": "Pandanggo sa Ilaw",
    "Palosebo": "Palosebo Climber",
    "Pabitin": "Pabitin Grabber",
    "Basaan": "Basaan Splash",
    "Bibingka": "Bibingka Baker",
    "Banda": "Banda Drummer",
    "Palayok": "Pukpok Palayok",
    "Sagala": "Sagala Arch",
    "Balut": "Balut Vendor",
    "Saranggola": "Saranggola Flyer",
    "Harana": "Harana Singer",
}
FIESTA_BASE_R = {"Tinikling": 0.10, "ColorGame": 0.09, "Pabitin": 0.085, "Sagala": 0.095, "Palayok": 0.09, "Bibingka": 0.085,
                 "Saranggola": 0.085, "Palosebo": 0.08}
FIESTA_POSE = {"Pandanggo": "stand", "Tinikling": "stand", "Sagala": "stand", "Harana": None}


def fiesta_prop(B, theme, key, c, s, y0, hand, head_top):
    """The prop of one of the new Fiesta figures. B: a Builder on the figure's atlas."""
    m = B.m
    A = B.A
    if theme == "Mani":
        bz = 0.36
        B.lathe([(0.0, 0.0), (0.13, 0.0), (0.18, 0.10), (0.19, 0.12), (0.0, 0.12)], "rope", base=(0, y0, bz * s), nu=20, scale=s)
        for k, (x, z) in enumerate(((-0.07, 0.0), (0.07, 0.02), (0.0, -0.08))):
            base = (x * s, y0 + 0.09 * s, (bz + z) * s)
            B.lathe([(0.0, 0.0), (0.05, 0.11), (0.0, 0.115)], "white", base=base, nu=12, scale=s)
            B.ellipsoid((base[0], base[1] + 0.12 * s, base[2]), (0.045 * s, 0.025 * s, 0.045 * s), "cone", nu=10, nv=6)
    elif theme == "Tinikling":
        for z in (-0.20, 0.30):
            m.bar((-0.72 * s, y0 + 0.035 * s, z * s), (0.72 * s, y0 + 0.035 * s, z * s), 0.06 * s, 0.06 * s, A.uv("bamboo"))
    elif theme == "Sampaguita":
        hx, hy, hz = hand
        for k, (r, drop) in enumerate(((0.15, 0.36), (0.13, 0.30), (0.11, 0.24))):   # three garlands hanging from the paw
            for i in range(18):
                a = TAU * i / 18
                p = (hx + (0.06 + k * 0.05) * s, hy - (drop * 0.5) * s * (1 - math.cos(a)) + 0.04 * s, hz + 0.06 * s + r * math.sin(a) * s * 0.7)
                B.ellipsoid(p, (0.03 * s, 0.03 * s, 0.03 * s), "white" if i % 5 else "leafgreen", nu=7, nv=5)
    elif theme == "ColorGame":
        x0, x1, z0, z1 = -0.62, -0.30, 0.0, 0.32
        m.box(x0 * s, x1 * s, y0, y0 + 0.32 * s, z0 * s, z1 * s, A.uv("red"), top=A.uv("yellow"), front=A.uv("ube"), right=A.uv("leafgreen"),
              left=A.uv("water"), back=A.uv("pinkprop"))
        for (x, z) in ((-0.52, 0.10), (-0.40, 0.22)):
            B.ellipsoid((x * s, y0 + 0.325 * s, z * s), (0.03 * s, 0.008 * s, 0.03 * s), "white", nu=8, nv=4)
        B.ellipsoid((0.30 * s, y0 + 0.45 * s, 0.12 * s), (0.05 * s, 0.05 * s, 0.05 * s), "gold", nu=10, nv=6)  # a winning token held up
    elif theme == "Fishball":
        hx, hy, hz = hand
        m.bar((hx, hy - 0.04 * s, hz + 0.05 * s), (hx + 0.03 * s, hy + 0.48 * s, hz + 0.08 * s), 0.012 * s, 0.012 * s, A.uv("wood"))
        for k in range(4):
            B.ellipsoid((hx + (0.01 + k * 0.0055) * s, hy + (0.18 + k * 0.085) * s, hz + (0.06 + k * 0.006) * s), (0.045 * s, 0.045 * s, 0.045 * s),
                        "cone", nu=12, nv=8)
        B.lathe([(0.0, 0.0), (0.05, 0.0), (0.065, 0.12), (0.0, 0.12)], "white", base=(-0.30 * s, y0 + 0.20 * s, 0.14 * s), nu=12, scale=s)
        B.ellipsoid((-0.30 * s, y0 + 0.32 * s, 0.14 * s), (0.06 * s, 0.01 * s, 0.06 * s), "clay", nu=10, nv=4)
    elif theme == "Pandanggo":
        spots = [(0.0, head_top + 0.0, 0.0), (0.36, 0.42, 0.10), (-0.36, 0.42, 0.10)]
        for (x, y, z) in spots:
            base = (x * s, y0 + y * s, z * s)
            B.lathe([(0.0, 0.0), (0.06, 0.0), (0.065, 0.06), (0.04, 0.09), (0.0, 0.09)], "glassy", base=base, nu=14, scale=s)
            B.lathe([(0.0, 0.0), (0.03, 0.02), (0.02, 0.06), (0.0, 0.10)], "yellow", base=(base[0], base[1] + 0.085 * s, base[2]), nu=10, scale=s)
            B.lathe([(0.0, 0.0), (0.014, 0.02), (0.0, 0.06)], "red", base=(base[0], base[1] + 0.10 * s, base[2] + 0.005 * s), nu=8, scale=s)
    elif theme == "Palosebo":
        x, z = 0.36, -0.10
        m.bar((x * s, y0, z * s), (x * s, y0 + 1.45 * s, z * s), 0.08 * s, 0.08 * s, A.uv("bamboo"))
        for k in range(5):
            m.bar(((x - 0.045) * s, y0 + (0.25 + k * 0.25) * s, z * s), ((x + 0.045) * s, y0 + (0.25 + k * 0.25) * s, z * s), 0.02 * s, 0.09 * s,
                  A.uv("darkwood"))
        B.ellipsoid((x * s, y0 + 1.48 * s, z * s), (0.09 * s, 0.10 * s, 0.09 * s), "pinkprop", nu=12, nv=8)   # the prize bag
        m.quad([((x + 0.02) * s, y0 + 1.30 * s, z * s), ((x + 0.24) * s, y0 + 1.36 * s, z * s), ((x + 0.24) * s, y0 + 1.46 * s, z * s),
                ((x + 0.02) * s, y0 + 1.44 * s, z * s)], A.uv("red"), two_sided=True)
    elif theme == "Pabitin":
        h = 1.32
        m.bar((0, y0, -0.46 * s), (0, y0 + (h + 0.20) * s, -0.46 * s), 0.05 * s, 0.05 * s, A.uv("bamboo"))
        m.bar((0, y0 + (h + 0.18) * s, -0.46 * s), (0, y0 + (h + 0.18) * s, 0.0), 0.04 * s, 0.04 * s, A.uv("bamboo"))
        m.bar((0, y0 + (h + 0.18) * s, 0.0), (0, y0 + h * s, 0.0), 0.012 * s, 0.012 * s, A.uv("rope"))
        q = 0.40
        corners = [(-q, -q), (q, -q), (q, q), (-q, q)]
        for i in range(4):
            a, b = corners[i], corners[(i + 1) % 4]
            m.bar((a[0] * s, y0 + h * s, a[1] * s), (b[0] * s, y0 + h * s, b[1] * s), 0.035 * s, 0.035 * s, A.uv("bamboo"))
        cols = ["red", "yellow", "ube", "leafgreen", "pinkprop", "water"]
        k = 0
        for xx in (-0.27, 0.0, 0.27):
            for zz in (-0.27, 0.27):
                drop = 0.18 + 0.06 * (k % 2)
                m.bar((xx * s, y0 + h * s, zz * s), (xx * s, y0 + (h - drop) * s, zz * s), 0.008 * s, 0.008 * s, A.uv("rope"))
                B.ellipsoid((xx * s, y0 + (h - drop - 0.04) * s, zz * s), (0.05 * s, 0.035 * s, 0.035 * s), cols[k % len(cols)], nu=10, nv=6)
                k += 1
    elif theme == "Basaan":
        B.lathe([(0.0, 0.0), (0.11, 0.0), (0.14, 0.20), (0.0, 0.20)], "water", base=(-0.42 * s, y0, 0.10 * s), nu=18, scale=s)
        B.lathe([(0.0, 0.0), (0.12, 0.0), (0.0, 0.002)], "glassy", base=(-0.42 * s, y0 + 0.195 * s, 0.10 * s), nu=18, scale=s)
        hx, hy, hz = hand
        B.lathe([(0.0, 0.0), (0.05, 0.0), (0.065, 0.07), (0.0, 0.07)], "red", base=(hx + 0.02 * s, hy + 0.10 * s, hz + 0.05 * s), rot=rot_xyz(rz=40), nu=12, scale=s)
        m.bar((hx, hy, hz + 0.04 * s), (hx + 0.02 * s, hy + 0.12 * s, hz + 0.05 * s), 0.015 * s, 0.015 * s, A.uv("red"))
        for (dx, dy, dz, r) in ((-0.02, 0.26, 0.10, 0.03), (-0.10, 0.32, 0.12, 0.025), (0.05, 0.36, 0.14, 0.02), (-0.16, 0.24, 0.16, 0.02)):
            B.ellipsoid((hx + dx * s, hy + dy * s, hz + dz * s), (r * s, r * 1.3 * s, r * s), "water", nu=8, nv=6)
    elif theme == "Bibingka":
        bx, bz = 0.42, 0.18
        for k in range(3):
            a = TAU * k / 3
            m.bar(((bx + 0.10 * math.cos(a)) * s, y0, (bz + 0.10 * math.sin(a)) * s), ((bx + 0.07 * math.cos(a)) * s, y0 + 0.14 * s, (bz + 0.07 * math.sin(a)) * s),
                  0.02 * s, 0.02 * s, A.uv("darkwood"))
        B.lathe([(0.0, 0.0), (0.12, 0.0), (0.15, 0.06), (0.0, 0.06)], "clay", base=(bx * s, y0 + 0.14 * s, bz * s), nu=18, scale=s)
        B.lathe([(0.0, 0.0), (0.13, 0.0), (0.12, 0.02), (0.0, 0.02)], "leafgreen", base=(bx * s, y0 + 0.20 * s, bz * s), nu=18, scale=s)
        B.lathe([(0.0, 0.0), (0.105, 0.0), (0.10, 0.035), (0.0, 0.04)], "cone", base=(bx * s, y0 + 0.21 * s, bz * s), nu=18, scale=s)
        for k in range(4):
            a = TAU * k / 4 + 0.4
            B.ellipsoid(((bx + 0.05 * math.cos(a)) * s, y0 + 0.255 * s, (bz + 0.05 * math.sin(a)) * s), (0.025 * s, 0.015 * s, 0.025 * s),
                        "black" if k % 2 else "red", nu=8, nv=5)  # hot coals on top
    elif theme == "Banda":
        B.lathe([(0.0, 0.0), (0.16, 0.0), (0.16, 0.12), (0.0, 0.12)], "red", base=(0, y0 + 0.16 * s, 0.33 * s), nu=24, scale=s)
        B.lathe([(0.0, 0.0), (0.162, 0.0), (0.0, 0.003)], "drumtop", base=(0, y0 + 0.28 * s, 0.33 * s), nu=24, scale=s)
        for side in (-1, 1):
            m.bar((side * 0.24 * s, y0 + 0.36 * s, 0.14 * s), (side * 0.06 * s, y0 + 0.30 * s, 0.38 * s), 0.016 * s, 0.016 * s, A.uv("wood"))
        m.bar((-0.17 * s, y0 + 0.45 * s, 0.05 * s), (0.17 * s, y0 + 0.22 * s, 0.30 * s), 0.03 * s, 0.006 * s, A.uv("white"))  # drum sling
    elif theme == "Palayok":
        hx, hy, hz = c["head"]
        hy_c = head_top - hy
        B.lathe([(0.0, -0.055), (hx + 0.018, -0.055), (hx + 0.03, 0.0), (hx + 0.018, 0.055), (0.0, 0.055)], "red",
                base=(0, y0 + (hy_c + 0.005) * s, 0.01 * s), nu=30, scale=s)   # the blindfold, over the eyes
        hx2, hy2, hz2 = hand
        m.bar((hx2, hy2 - 0.02 * s, hz2 + 0.03 * s), (hx2 + 0.10 * s, hy2 + 0.75 * s, hz2 + 0.10 * s), 0.03 * s, 0.03 * s, A.uv("wood"))
        px, pz = -0.62, -0.10
        m.bar((px * s, y0, pz * s), (px * s, y0 + 1.65 * s, pz * s), 0.05 * s, 0.05 * s, A.uv("darkwood"))
        m.bar((px * s, y0 + 1.62 * s, pz * s), (0.02 * s, y0 + 1.62 * s, 0.20 * s), 0.04 * s, 0.04 * s, A.uv("darkwood"))
        m.bar((0.02 * s, y0 + 1.62 * s, 0.20 * s), (0.02 * s, y0 + 1.42 * s, 0.20 * s), 0.01 * s, 0.01 * s, A.uv("rope"))
        B.lathe([(0.0, 0.0), (0.09, 0.03), (0.12, 0.10), (0.08, 0.17), (0.07, 0.19), (0.0, 0.19)], "clay",
                base=(0.02 * s, y0 + 1.24 * s, 0.20 * s), nu=18, scale=s)
    elif theme == "Sagala":
        R0 = 0.66
        z = 0.04
        n = 15
        for i in range(n):
            a = math.pi * i / (n - 1)
            p = (R0 * math.cos(a) * s, y0 + R0 * 1.55 * math.sin(a) * s, z * s)
            if i < n - 1:
                a2 = math.pi * (i + 1) / (n - 1)
                q = (R0 * math.cos(a2) * s, y0 + R0 * 1.55 * math.sin(a2) * s, z * s)
                m.bar(p, q, 0.03 * s, 0.03 * s, A.uv("bamboo"))
            if 0 < i < n - 1:
                _flower(B, (p[0], p[1], p[2] + 0.03 * s), 0.06 * s, ["accent", "white", "yellow", "pinkprop"][i % 4], normal=(0, 0.2, 1))
                B.ellipsoid((p[0], p[1], p[2] - 0.02 * s), (0.05 * s, 0.03 * s, 0.03 * s), "leafgreen", rot=rot_xyz(rz=math.degrees(a)), nu=8, nv=5)
    elif theme == "Balut":
        bz = 0.36
        B.lathe([(0.0, 0.0), (0.14, 0.0), (0.17, 0.11), (0.0, 0.11)], "rope", base=(0, y0, bz * s), nu=20, scale=s)
        B.lathe([(0.0, 0.0), (0.16, 0.0), (0.0, 0.01)], "white", base=(0, y0 + 0.11 * s, bz * s), nu=20, scale=s)  # cloth over the eggs
        for (x, z) in ((-0.06, 0.03), (0.05, -0.04), (0.06, 0.07), (-0.04, -0.07), (0.0, 0.0)):
            B.ellipsoid((x * s, y0 + 0.15 * s, (bz + z) * s), (0.04 * s, 0.05 * s, 0.04 * s), "cream", nu=10, nv=6)
        lx, lz = -0.42, 0.06
        B.lathe([(0.0, 0.0), (0.06, 0.0), (0.06, 0.03), (0.04, 0.04), (0.055, 0.12), (0.03, 0.17), (0.0, 0.18)], "glassy",
                base=(lx * s, y0, lz * s), nu=14, scale=s)
        B.ellipsoid((lx * s, y0 + 0.09 * s, lz * s), (0.03 * s, 0.035 * s, 0.03 * s), "yellow", nu=8, nv=6)
    elif theme == "Saranggola":
        hx, hy, hz = hand
        kc = np.array([0.52 * s, y0 + 1.30 * s, -0.10 * s])
        w, h = 0.24 * s, 0.32 * s
        pts = [kc + np.array([0, -h, 0]), kc + np.array([w, 0, 0]), kc + np.array([0, h * 0.7, 0]), kc + np.array([-w, 0, 0])]
        m.quad([tuple(p) for p in pts], A.uv("kite"), two_sided=True)
        m.bar(tuple(kc + np.array([0, -h, 0.005 * s])), tuple(kc + np.array([0, h * 0.7, 0.005 * s])), 0.01 * s, 0.01 * s, A.uv("darkwood"))
        m.bar((hx, hy, hz), tuple(kc + np.array([0, -0.05 * s, 0])), 0.006 * s, 0.006 * s, A.uv("white"))
        tail = kc + np.array([0, -h, 0])
        for k in range(4):
            a = tail + np.array([-0.03 * s * k, -0.09 * s * k, 0])
            b = tail + np.array([-0.03 * s * (k + 1), -0.09 * s * (k + 1), 0])
            m.bar(tuple(a), tuple(b), 0.006 * s, 0.006 * s, A.uv("rope"))
            B.ellipsoid(tuple(b), (0.025 * s, 0.012 * s, 0.01 * s), ["red", "yellow", "water", "leafgreen"][k], nu=8, nv=4)
    elif theme == "Harana":
        gx, gy, gz = 0.02, 0.30, 0.30
        R = rot_xyz(rz=-35)
        B.ellipsoid((gx * s, y0 + gy * s, gz * s), (0.13 * s, 0.15 * s, 0.05 * s), "wood", rot=R, nu=16, nv=8)
        up = R @ np.array([0, 1.0, 0])
        cen = np.array([gx * s, y0 + gy * s, gz * s])
        B.ellipsoid(tuple(cen + up * 0.16 * s), (0.10 * s, 0.11 * s, 0.045 * s), "wood", rot=R, nu=14, nv=8)
        B.ellipsoid(tuple(cen + up * 0.13 * s + np.array([0, 0, 0.045 * s])), (0.035 * s, 0.035 * s, 0.006 * s), "black", rot=R, nu=10, nv=5)
        m.bar(tuple(cen + up * 0.24 * s), tuple(cen + up * 0.62 * s), 0.035 * s, 0.025 * s, A.uv("darkwood"), up=(0, 0, 1))
        m.bar(tuple(cen + up * 0.61 * s), tuple(cen + up * 0.72 * s), 0.05 * s, 0.025 * s, A.uv("darkwood"), up=(0, 0, 1))
        _flower(B, (0.30 * s, y0 + 0.62 * s, 0.10 * s), 0.05 * s, "red", normal=(0.3, 0.2, 1))   # a rose for the window
    else:
        raise ValueError(theme)
