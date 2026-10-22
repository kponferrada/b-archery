"""Jamie's Treasures - Treasured Blades (0.5.0): 20 original glowing swords.

Every blade is built in the SAME frame as the game's own Katana mesh
(media/models_X/weapons/2handed/Katana.x, read from the 42.21 install):
    handle from y = -0.05 to 0.115, guard at y ~0.12, blade to y ~0.576,
    blade in the y/z plane (curving toward +z), thickness along x, metres.
so the Katana's own hand / world attachment points (copied into each model
script) hold and drop it exactly like the Katana.

Texture: one 512 x 512 per blade, two columns:
    u <  0.734  normal texels (lit by the scene like any item)
    u >= 0.766  GLOW texels (drawn at full brightness by the jt_glow shader,
                dev/make_shaders.py; the shader's line is u = 0.75, with a
                margin so mipmaps never blend the two columns)
The cutting edge bevels, the fuller line and gems use glow texels, so the
glow follows the blade in hand, on the back and on the floor.

All designs are original (Jamie's briefs in docs/BLADES.md); none copies a
weapon from a game, anime or film.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import core
import kawaii as K
import meadow as MW

TAU = 2 * math.pi
SIZE = 512
NORMAL_W = 376          # x < 376 (u < 0.734)
GLOW_X0 = 392           # x >= 392 (u >= 0.766)
GLOW_U = 0.75

# the Katana's frame (from Katana.x)
HANDLE_Y0, HANDLE_Y1 = -0.050, 0.112
GUARD_Y = 0.118
BLADE_Y0, BLADE_LEN = 0.126, 0.450


# =========================================================================== the 20 designs
# blade: steel colour; glow: glow colour; guard / accent / wrap colours; shapes.
#   curve   tip offset toward +z as a share of the length (katana ~0.035)
#   width   blade width at the base (m), tip: "kissaki" | "point" | "clip"
#   guard   guard style, pommel: pommel style, engrave: glowing pattern in the fuller
DESIGNS = [
    dict(key="CrimsonEclipse", name="Crimson Eclipse", rarity="Legendary",
         lore="A black blade that burns crimson at the edge, under a gold crescent.",
         blade=(30, 26, 32), glow=(235, 30, 52), guard_col=(222, 172, 58), accent=(222, 172, 58),
         wrap=(26, 22, 26), wrap2=(150, 24, 36), curve=0.035, width=0.030, tip="kissaki",
         guard="crescent", pommel="cap", engrave="line"),
    dict(key="Frostveil", name="Frostveil", rarity="Legendary",
         lore="Silver-blue steel with an icy glow and a guard grown from crystal.",
         blade=(170, 192, 214), glow=(110, 200, 255), guard_col=(196, 230, 250), accent=(150, 186, 214),
         wrap=(60, 80, 110), wrap2=(200, 226, 245), curve=0.0, width=0.052, tip="point",
         guard="crystal", pommel="crystal", engrave="frost",
         # oversized (0.5.3): ~1.35x the Legendary Katana's overall length, ~1.7x its width
         blade_len=0.640, thick=0.0058, handle_len=0.185, handle_r=0.0135, profile="broad"),
    dict(key="SakuraRequiem", name="Sakura Requiem", rarity="Legendary",
         lore="Ivory fittings, rose-gold metal and a soft rose-pink glow.",
         blade=(214, 206, 210), glow=(255, 120, 170), guard_col=(222, 156, 132), accent=(222, 156, 132),
         wrap=(244, 236, 222), wrap2=(222, 156, 132), curve=0.035, width=0.028, tip="kissaki",
         guard="blossom", pommel="cap", engrave="petals"),
    dict(key="VoidCrescent", name="Void Crescent", rarity="Legendary",
         lore="A dark blade with a violet glow under a guard shaped like a waning moon.",
         blade=(40, 34, 56), glow=(170, 90, 255), guard_col=(150, 150, 170), accent=(120, 110, 150),
         wrap=(30, 26, 44), wrap2=(110, 80, 170), curve=0.03, width=0.030, tip="kissaki",
         guard="moon", pommel="ring", engrave="line"),
    dict(key="Dawnbringer", name="Dawnbringer", rarity="Legendary",
         lore="Gold-trimmed steel glowing warm gold behind a sunburst guard.",
         blade=(206, 200, 186), glow=(255, 196, 70), guard_col=(236, 186, 60), accent=(236, 186, 60),
         wrap=(240, 230, 210), wrap2=(200, 150, 50), curve=0.0, width=0.034, tip="point",
         guard="sunburst", pommel="sun", engrave="rays"),
    dict(key="Stormcaller", name="Stormcaller", rarity="Legendary",
         lore="Storm-blue steel with lightning engraved along it, crackling electric blue.",
         blade=(60, 82, 120), glow=(90, 170, 255), guard_col=(150, 170, 200), accent=(90, 120, 170),
         wrap=(30, 40, 66), wrap2=(120, 170, 240), curve=0.02, width=0.030, tip="clip",
         guard="bolt", pommel="cap", engrave="lightning"),
    dict(key="Emberfang", name="Emberfang", rarity="Legendary",
         lore="Black steel with an ember-orange edge like a coal that never cools.",
         blade=(34, 30, 30), glow=(255, 120, 30), guard_col=(60, 54, 52), accent=(140, 70, 30),
         wrap=(30, 26, 24), wrap2=(170, 70, 20), curve=0.03, width=0.032, tip="clip",
         guard="fang", pommel="fang", engrave="embers"),
    dict(key="SerpentsWhisper", name="Serpent's Whisper", rarity="Legendary",
         lore="Emerald fittings, an emerald glow, and a coiled serpent for a guard.",
         blade=(150, 170, 160), glow=(40, 230, 120), guard_col=(30, 140, 80), accent=(40, 160, 90),
         wrap=(20, 50, 34), wrap2=(60, 190, 110), curve=0.03, width=0.028, tip="kissaki",
         guard="serpent", pommel="gem", engrave="scales"),
    dict(key="Starfall", name="Starfall", rarity="Legendary",
         lore="Silver steel with a cool white glow and stars engraved along it.",
         blade=(196, 200, 210), glow=(225, 238, 255), guard_col=(206, 210, 222), accent=(170, 176, 196),
         wrap=(44, 50, 80), wrap2=(200, 206, 230), curve=0.0, width=0.032, tip="point",
         guard="star", pommel="star", engrave="stars"),
    dict(key="Bloodmoon", name="Bloodmoon", rarity="Legendary",
         lore="Dark fittings, crimson ornaments and a deep-crimson glow.",
         blade=(64, 50, 54), glow=(170, 10, 30), guard_col=(50, 40, 44), accent=(150, 20, 36),
         wrap=(40, 30, 32), wrap2=(130, 16, 30), curve=0.035, width=0.030, tip="kissaki",
         guard="fullmoon", pommel="ring", engrave="line"),
    dict(key="JadePhantom", name="Jade Phantom", rarity="Legendary",
         lore="A jade-green handle on dark fittings, glowing jade.",
         blade=(120, 140, 132), glow=(60, 220, 150), guard_col=(40, 46, 44), accent=(60, 150, 110),
         wrap=(50, 140, 100), wrap2=(26, 70, 50), curve=0.025, width=0.028, tip="kissaki",
         guard="square", pommel="cap", engrave="line"),
    dict(key="SunkenRelic", name="Sunken Relic", rarity="Legendary",
         lore="Weathered steel and ocean motifs under a muted teal glow.",
         blade=(120, 130, 128), glow=(70, 190, 180), guard_col=(110, 120, 104), accent=(80, 140, 130),
         wrap=(60, 80, 76), wrap2=(110, 150, 140), curve=0.015, width=0.032, tip="point",
         guard="wave", pommel="shell", engrave="waves"),
    dict(key="DragonsOath", name="Dragon's Oath", rarity="Legendary",
         lore="A guard of spread bronze wings and a bronze-gold glow.",
         blade=(176, 166, 150), glow=(240, 170, 70), guard_col=(176, 120, 60), accent=(196, 140, 70),
         wrap=(70, 40, 24), wrap2=(176, 120, 60), curve=0.0, width=0.036, tip="point",
         guard="wings", pommel="claw", engrave="line"),
    dict(key="Moonflower", name="Moonflower", rarity="Legendary",
         lore="Lavender accents and floral engravings with a soft lavender glow.",
         blade=(204, 200, 214), glow=(200, 160, 255), guard_col=(190, 170, 220), accent=(170, 140, 210),
         wrap=(90, 70, 120), wrap2=(200, 180, 236), curve=0.03, width=0.028, tip="kissaki",
         guard="flower", pommel="bud", engrave="vines"),
    dict(key="ObsidianCrown", name="Obsidian Crown", rarity="Legendary",
         lore="A black blade, silver ornaments and a deep-purple glow under a crowned guard.",
         blade=(24, 22, 30), glow=(130, 40, 220), guard_col=(200, 204, 214), accent=(200, 204, 214),
         wrap=(20, 18, 24), wrap2=(170, 170, 186), curve=0.0, width=0.034, tip="point",
         guard="crown", pommel="crown", engrave="line"),
    dict(key="GoldenKoi", name="Golden Koi", rarity="Legendary",
         lore="Gold-and-red fittings shaped like koi fins, glowing warm gold.",
         blade=(206, 196, 176), glow=(255, 190, 60), guard_col=(232, 180, 60), accent=(210, 50, 40),
         wrap=(190, 40, 34), wrap2=(240, 200, 90), curve=0.03, width=0.030, tip="kissaki",
         guard="koi", pommel="fin", engrave="scales"),
    dict(key="SpiritLantern", name="Spirit Lantern", rarity="Legendary",
         lore="Pale steel and a little lantern for a pommel, glowing lantern gold.",
         blade=(214, 214, 206), glow=(255, 206, 110), guard_col=(150, 120, 90), accent=(110, 80, 60),
         wrap=(220, 210, 190), wrap2=(110, 80, 60), curve=0.025, width=0.028, tip="kissaki",
         guard="round", pommel="lantern", engrave="line"),
    dict(key="ThunderOni", name="Thunder Oni", rarity="Legendary",
         lore="Red-and-black fittings, two horns for a guard and a red-violet glow.",
         blade=(50, 40, 44), glow=(230, 60, 170), guard_col=(30, 24, 26), accent=(200, 30, 40),
         wrap=(190, 30, 36), wrap2=(26, 22, 24), curve=0.035, width=0.032, tip="clip",
         guard="horns", pommel="cap", engrave="lightning"),
    dict(key="CelestialThread", name="Celestial Thread", rarity="Legendary",
         lore="Silver steel threaded with fine blue lines and a pale-cyan glow.",
         blade=(200, 206, 214), glow=(150, 240, 255), guard_col=(196, 200, 214), accent=(80, 130, 220),
         wrap=(40, 60, 110), wrap2=(140, 200, 250), curve=0.02, width=0.026, tip="kissaki",
         guard="thread", pommel="ring", engrave="threads"),
    dict(key="LastEmber", name="Last Ember", rarity="Legendary",
         lore="Battle-scarred and notched, still glowing a warm orange ember.",
         blade=(110, 100, 94), glow=(255, 140, 50), guard_col=(80, 70, 64), accent=(120, 80, 50),
         wrap=(70, 50, 40), wrap2=(110, 80, 60), curve=0.03, width=0.031, tip="kissaki",
         guard="chipped", pommel="cap", engrave="cracks", scarred=True),
]
# Oversized (0.6.0, Jamie's brief): every blade after Crimson Eclipse is about 1.3-1.5x the
# Legendary Katana's overall length (0.627 m), wider and thicker, each with its own
# proportions. blade_len: blade length (Legendary Katana 0.45), width at the base (0.030),
# thick: half-thickness (0.0042), handle_len (0.162), profile: taper | broad | leaf.
# Only the model changes: combat comes from the Legendary Katana (dev/catalog.py KATANA).
SIZES = {
    "SakuraRequiem":   dict(blade_len=0.600, width=0.040, thick=0.0052, handle_len=0.190, profile="taper", curve=0.030),
    "VoidCrescent":    dict(blade_len=0.620, width=0.046, thick=0.0055, handle_len=0.185, profile="leaf", curve=0.020),
    "Dawnbringer":     dict(blade_len=0.640, width=0.058, thick=0.0062, handle_len=0.195, profile="broad"),
    "Stormcaller":     dict(blade_len=0.600, width=0.044, thick=0.0054, handle_len=0.185, profile="taper"),
    "Emberfang":       dict(blade_len=0.620, width=0.050, thick=0.0058, handle_len=0.185, profile="leaf", curve=0.020),
    "SerpentsWhisper": dict(blade_len=0.600, width=0.040, thick=0.0052, handle_len=0.185, profile="taper"),
    "Starfall":        dict(blade_len=0.640, width=0.050, thick=0.0058, handle_len=0.190, profile="broad"),
    "Bloodmoon":       dict(blade_len=0.620, width=0.048, thick=0.0056, handle_len=0.190, profile="taper"),
    "JadePhantom":     dict(blade_len=0.600, width=0.040, thick=0.0052, handle_len=0.185, profile="taper"),
    "SunkenRelic":     dict(blade_len=0.580, width=0.054, thick=0.0060, handle_len=0.180, profile="broad"),
    "DragonsOath":     dict(blade_len=0.660, width=0.060, thick=0.0064, handle_len=0.200, profile="broad"),
    "Moonflower":      dict(blade_len=0.600, width=0.040, thick=0.0052, handle_len=0.185, profile="leaf", curve=0.025),
    "ObsidianCrown":   dict(blade_len=0.660, width=0.058, thick=0.0062, handle_len=0.200, profile="broad"),
    "GoldenKoi":       dict(blade_len=0.600, width=0.044, thick=0.0054, handle_len=0.185, profile="leaf"),
    "SpiritLantern":   dict(blade_len=0.580, width=0.040, thick=0.0052, handle_len=0.175, profile="taper"),
    "ThunderOni":      dict(blade_len=0.640, width=0.052, thick=0.0060, handle_len=0.195, profile="broad"),
    "CelestialThread": dict(blade_len=0.620, width=0.036, thick=0.0050, handle_len=0.185, profile="taper"),
    "LastEmber":       dict(blade_len=0.600, width=0.046, thick=0.0056, handle_len=0.185, profile="taper"),
}
for _d in DESIGNS:
    _d.update(SIZES.get(_d["key"], {}))
BY_KEY = {d["key"]: d for d in DESIGNS}


def item_id(key):
    return "JT_Blade_" + key


# =========================================================================== atlas with a glow column
class GlowAtlas:
    """Like core.Atlas (same uv/point interface for kawaii.Builder), but with two
    columns: normal regions left, glow regions right (see the module notes)."""
    BLEED = 3

    def __init__(self, background=(40, 40, 44, 255)):
        self.size = SIZE
        self.img = Image.new("RGBA", (SIZE, SIZE), background)
        self.R = {}
        self._pending = []
        self.glow = set()

    def add(self, name, image, glow=False):
        if name in self.R or any(n == name for n, _, _ in self._pending):
            raise ValueError("duplicate region " + name)
        self._pending.append((name, image.convert("RGBA"), glow))

    def finish(self):
        b = self.BLEED
        for column, (x0, x1) in ((False, (0, NORMAL_W)), (True, (GLOW_X0, SIZE))):
            x, y, rowh = x0, 0, 0
            items = sorted([p for p in self._pending if p[2] == column], key=lambda p: (-p[1].height, -p[1].width, p[0]))
            for name, im, _ in items:
                w, h = im.size
                if w + 2 * b > x1 - x0:
                    raise ValueError("region %s too wide for its column" % name)
                if x + w + 2 * b > x1:
                    x, y, rowh = x0, y + rowh, 0
                if y + h + 2 * b > SIZE:
                    raise ValueError("glow atlas full at " + name)
                px, py = x + b, y + b
                self.img.paste(im.resize((w + 2 * b, h + 2 * b), Image.NEAREST), (px - b, py - b))
                op = im.copy()
                op.putalpha(255)
                self.img.paste(op, (px, py))
                self.R[name] = (px, py, w, h)
                if column:
                    self.glow.add(name)
                x += w + 2 * b
                rowh = max(rowh, h + 2 * b)
        self._pending = []
        return self

    def uv(self, name, sub=(0, 0, 1, 1), flip=False, rot=0, inset=0.75):
        return core.Atlas.uv(self, name, sub, flip, rot, inset)

    def point(self, name, u, v):
        return core.Atlas.point(self, name, u, v)


# =========================================================================== textures
def _grad(c, w, h, top=1.10, bottom=0.86, horizontal=False):
    im = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(im)
    n = w if horizontal else h
    for i in range(n):
        k = top + (bottom - top) * i / max(1, n - 1)
        col = tuple(max(0, min(255, int(v * k))) for v in c) + (255,)
        if horizontal:
            d.line([(i, 0), (i, h)], fill=col)
        else:
            d.line([(0, i), (w, i)], fill=col)
    return im


def _mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def blade_face_tex(d, w=96, h=256):
    """The flat of the blade: u across (spine -> ridge), v along (tip at the top)."""
    c = d["blade"]
    im = _grad(c, w, h, 1.18, 0.92, horizontal=True)
    dr = ImageDraw.Draw(im)
    # a soft temper line near the ridge
    hl = _mix(c, (255, 255, 255), 0.22)
    pts = [(w - 14 + 5 * math.sin(i / 9.0), i) for i in range(0, h, 4)]
    dr.line(pts, fill=hl + (255,), width=3)
    if d.get("scarred"):
        rng = np.random.default_rng(7)
        for _ in range(26):
            x, y = rng.uniform(0, w), rng.uniform(0, h)
            L = rng.uniform(6, 20)
            a = rng.uniform(-0.6, 0.6)
            dr.line([(x, y), (x + L * math.cos(a), y + L * math.sin(a))], fill=_mix(c, (20, 16, 14), 0.5) + (255,), width=1)
    return im


def glow_edge_tex(d, w=48, h=256):
    """The edge bevel: u from the ridge (glow colour) to the cutting edge (white-hot core)."""
    g = d["glow"]
    im = Image.new("RGBA", (w, h))
    dr = ImageDraw.Draw(im)
    for x in range(w):
        t = x / (w - 1)
        col = _mix(_mix(g, (0, 0, 0), 0.10), _mix(g, (255, 255, 255), 0.55), t ** 1.6)
        dr.line([(x, 0), (x, h)], fill=col + (255,))
    if d.get("scarred"):   # cooler, darker notches along the worn edge
        for y in range(8, h, 37):
            dr.rectangle([w - 10, y, w, y + 5], fill=_mix(g, (60, 30, 10), 0.6) + (255,))
    return im


def glow_fuller_tex(d, w=32, h=256):
    """The glowing groove on both flats: u across, v along. The engraving pattern lives here."""
    g = d["glow"]
    core_c = _mix(g, (255, 255, 255), 0.6)
    im = Image.new("RGBA", (w, h), _mix(g, (0, 0, 0), 0.35) + (255,))
    dr = ImageDraw.Draw(im)
    e = d["engrave"]
    cx = w // 2
    if e in ("line", "embers", "cracks", "scales", "petals", "rays"):
        dr.rectangle([cx - 4, 0, cx + 4, h], fill=g + (255,))
        dr.rectangle([cx - 1, 0, cx + 1, h], fill=core_c + (255,))
        if e == "embers":
            rng = np.random.default_rng(3)
            for _ in range(30):
                x, y = rng.uniform(2, w - 2), rng.uniform(0, h)
                dr.ellipse([x - 2, y - 2, x + 2, y + 2], fill=core_c + (255,))
        if e == "petals":
            for y in range(10, h, 28):
                dr.ellipse([cx - 9, y - 5, cx + 9, y + 5], fill=g + (255,))
        if e == "rays":
            for y in range(6, h, 18):
                dr.polygon([(cx, y - 6), (cx + 9, y), (cx, y + 6), (cx - 9, y)], fill=core_c + (255,))
        if e == "scales":
            for y in range(0, h, 10):
                dr.arc([cx - 8, y - 4, cx + 8, y + 8], 200, 340, fill=core_c + (255,), width=2)
        if e == "cracks":
            rng = np.random.default_rng(11)
            for y in range(12, h, 30):
                x0 = cx + rng.uniform(-3, 3)
                dr.line([(x0, y), (x0 + rng.uniform(-10, 10), y + 8), (x0 + rng.uniform(-12, 12), y + 15)], fill=core_c + (255,), width=2)
    elif e == "lightning":
        pts = []
        for i, y in enumerate(range(0, h + 1, 14)):
            pts.append((cx + (8 if i % 2 else -8), y))
        dr.line(pts, fill=g + (255,), width=6)
        dr.line(pts, fill=core_c + (255,), width=2)
    elif e == "frost":
        dr.rectangle([cx - 3, 0, cx + 3, h], fill=g + (255,))
        for y in range(8, h, 22):
            for s in (-1, 1):
                dr.line([(cx, y), (cx + s * 10, y - 8)], fill=core_c + (255,), width=2)
    elif e == "stars":
        dr.rectangle([cx - 2, 0, cx + 2, h], fill=g + (255,))
        for y in range(10, h, 24):
            r = 7
            pts = []
            for k in range(8):
                rr = r if k % 2 == 0 else r * 0.35
                a = -math.pi / 2 + k * math.pi / 4
                pts.append((cx + rr * math.cos(a), y + rr * math.sin(a)))
            dr.polygon(pts, fill=core_c + (255,))
    elif e == "waves":
        pts = [(cx + 8 * math.sin(y / 7.0), y) for y in range(0, h + 1, 2)]
        dr.line(pts, fill=g + (255,), width=6)
        dr.line(pts, fill=core_c + (255,), width=2)
    elif e == "vines":
        pts = [(cx + 6 * math.sin(y / 11.0), y) for y in range(0, h + 1, 2)]
        dr.line(pts, fill=g + (255,), width=4)
        for y in range(14, h, 26):
            x = cx + 6 * math.sin(y / 11.0)
            dr.ellipse([x - 7, y - 4, x + 7, y + 4], fill=core_c + (255,))
    elif e == "threads":
        for k, off in enumerate((-7, 0, 7)):
            pts = [(cx + off + 3 * math.sin(y / 9.0 + k), y) for y in range(0, h + 1, 2)]
            dr.line(pts, fill=(core_c if k == 1 else g) + (255,), width=2)
    return im


def wrap_tex(d, w=96, h=128):
    """Handle wrap: diamond pattern (tsuka-ito style) in the two wrap colours."""
    a, b = d["wrap"], d["wrap2"]
    im = Image.new("RGBA", (w, h), a + (255,))
    dr = ImageDraw.Draw(im)
    step = 16
    for y in range(-step, h + step, step):
        for x in range(0, w + step, step):
            dr.polygon([(x, y), (x + step / 2, y + step / 2), (x, y + step), (x - step / 2, y + step / 2)], fill=b + (255,))
            dr.polygon([(x, y + 4), (x + step / 2 - 4, y + step / 2), (x, y + step - 4), (x - step / 2 + 4, y + step / 2)], fill=a + (255,))
    return im


def metal_tex(c, w=64, h=64, worn=False):
    im = _grad(c, w, h, 1.2, 0.8)
    if worn:
        dr = ImageDraw.Draw(im)
        rng = np.random.default_rng(5)
        for _ in range(40):
            x, y = rng.uniform(0, w), rng.uniform(0, h)
            dr.point((x, y), fill=_mix(c, (40, 60, 50), 0.6) + (255,))
    return im


def gem_tex(d, w=32, h=32):
    g = d["glow"]
    im = Image.new("RGBA", (w, h), g + (255,))
    dr = ImageDraw.Draw(im)
    dr.ellipse([w * 0.2, h * 0.15, w * 0.55, h * 0.5], fill=_mix(g, (255, 255, 255), 0.7) + (255,))
    return im


def make_atlas(d):
    A = GlowAtlas(background=d["blade"] + (255,))
    A.add("face", blade_face_tex(d))
    A.add("spine", metal_tex(_mix(d["blade"], (0, 0, 0), 0.25)))
    A.add("guard", metal_tex(d["guard_col"], worn=d["engrave"] == "waves" or d.get("scarred", False)))
    A.add("accent", metal_tex(d["accent"]))
    A.add("wrap", wrap_tex(d))
    A.add("dark", metal_tex(_mix(d["wrap"], (0, 0, 0), 0.4)))
    A.add("glow_edge", glow_edge_tex(d), glow=True)
    A.add("glow_fuller", glow_fuller_tex(d), glow=True)
    A.add("glow_gem", gem_tex(d), glow=True)
    return A.finish()


# =========================================================================== geometry
def _face(m, pts, uvs, centre):
    """A quad or triangle wound to face away from `centre`; degenerate corners dropped."""
    P = [np.array(p, dtype=float) for p in pts]
    keep = [0]
    for i in range(1, len(P)):
        if np.linalg.norm(P[i] - P[keep[-1]]) > 1e-7:
            keep.append(i)
    if len(keep) > 2 and np.linalg.norm(P[keep[-1]] - P[keep[0]]) < 1e-7:
        keep.pop()
    if len(keep) < 3:
        return
    P = [P[i] for i in keep]
    U = [uvs[i] for i in keep]
    n = np.cross(P[1] - P[0], P[2] - P[0])
    if len(P) == 4:
        n = n + np.cross(P[2] - P[0], P[3] - P[0])
    if np.linalg.norm(n) < 1e-12:
        return
    mid = np.mean(P, axis=0)
    if n @ (mid - np.asarray(centre, dtype=float)) < 0:
        P = P[::-1]
        U = U[::-1]
    if len(P) == 3:
        m.triangle(P, U)
    else:
        m.quad(P, U)


def blade_rings(d, n=34):
    """Cross-sections along the blade. Each ring: list of 5 (x, y, z) points
    [spine-left, spine-right, ridge-right, edge, ridge-left] and its t."""
    L = d.get("blade_len", BLADE_LEN)
    w0 = d["width"]
    h0 = d.get("thick", 0.0042)
    prof = d.get("profile", "taper")
    rings = []
    tip = d["tip"]
    ts = {"kissaki": 0.86, "point": 0.80, "clip": 0.82}[tip]
    for i in range(n + 1):
        t = i / n
        y = BLADE_Y0 + L * t
        zc = d["curve"] * L * t * t
        if prof == "broad":      # nearly parallel edges: a heavy fantasy blade
            w = w0 * (1.0 - 0.08 * t)
        elif prof == "leaf":     # swells toward the tip, then points
            w = w0 * (0.85 + 0.35 * math.sin(math.pi * min(1.0, t / 0.8) * 0.85))
        else:
            w = w0 * (1.0 - 0.22 * t)
        h = h0 * (1.0 - 0.45 * t)
        f = 1.0
        spine_drop = 0.0
        if t > ts:
            s = (t - ts) / (1 - ts)
            if tip == "kissaki":
                f = math.sqrt(max(0.0, 1 - s * s))           # the edge sweeps up to the spine
            elif tip == "point":
                f = 1 - s                                      # straight taper, spine taper too
                spine_drop = 0.5 * w * s
            else:  # clip point: the spine dips to meet the edge
                f = 1 - s
                spine_drop = w * s * 0.9
        spine = zc - w / 2 + spine_drop
        width = max(0.0, (w - spine_drop) * f) if tip != "kissaki" else w * f
        edge = spine + width
        ridge = spine + 0.62 * width
        hh = h * (f if t > ts else 1.0)
        if d.get("scarred") and 0.15 < t < 0.8 and i % 5 == 2:
            edge -= 0.0025     # a nick in the edge
        ring = [(-0.85 * hh, y, spine), (0.85 * hh, y, spine), (hh, y, ridge), (0.0, y, edge), (-hh, y, ridge)]
        if i == n:
            p = (0.0, y, spine)
            ring = [p] * 5
        rings.append((t, ring))
    return rings


def build_blade(m, A, d):
    rings = blade_rings(d)
    regions = ["spine", "face", "glow_edge", "glow_edge", "face"]
    for (t0, r0), (t1, r1) in zip(rings[:-1], rings[1:]):
        c0 = np.mean(r0, axis=0)
        c1 = np.mean(r1, axis=0)
        centre = (c0 + c1) / 2
        for k in range(5):
            a0, b0 = r0[k], r0[(k + 1) % 5]
            a1, b1 = r1[k], r1[(k + 1) % 5]
            reg = regions[k]
            v0, v1 = 1 - t0, 1 - t1         # tip at the top of the texture
            if k == 2:       # ridge -> edge: u 0 -> 1
                uv = [A.point(reg, 0.02, v0), A.point(reg, 0.98, v0), A.point(reg, 0.98, v1), A.point(reg, 0.02, v1)]
            elif k == 3:     # edge -> ridge
                uv = [A.point(reg, 0.98, v0), A.point(reg, 0.02, v0), A.point(reg, 0.02, v1), A.point(reg, 0.98, v1)]
            elif k == 1:     # spine -> ridge
                uv = [A.point(reg, 0.02, v0), A.point(reg, 0.98, v0), A.point(reg, 0.98, v1), A.point(reg, 0.02, v1)]
            elif k == 4:     # ridge -> spine
                uv = [A.point(reg, 0.98, v0), A.point(reg, 0.02, v0), A.point(reg, 0.02, v1), A.point(reg, 0.98, v1)]
            else:
                uv = [A.point(reg, 0.1, v0), A.point(reg, 0.9, v0), A.point(reg, 0.9, v1), A.point(reg, 0.1, v1)]
            _face(m, [a0, b0, b1, a1], uv, centre)
    # base cap (hidden in the collar, but closes the solid)
    t0, r0 = rings[0]
    c0 = np.mean(r0, axis=0) + np.array([0, -0.01, 0])
    for k in range(5):
        _face(m, [r0[k], r0[(k + 1) % 5], np.mean(r0, axis=0)], [A.point("spine", 0.5, 0.5)] * 3, c0)
    # the glowing fuller: a thin inlay on both flats
    for side in (-1, 1):
        strip = []
        for t, r in rings:
            if t < 0.05 or t > 0.72:
                continue
            sp, ri = np.array(r[0 if side < 0 else 1]), np.array(r[4 if side < 0 else 2])
            a = sp + (ri - sp) * 0.30
            b = sp + (ri - sp) * 0.62
            off = np.array([side * 0.0006, 0, 0])
            strip.append((t, a + off, b + off))
        for (t0, a0, b0), (t1, a1, b1) in zip(strip[:-1], strip[1:]):
            s0 = (t0 - 0.05) / 0.67
            s1 = (t1 - 0.05) / 0.67
            uv = [A.point("glow_fuller", 0.05, 1 - s0), A.point("glow_fuller", 0.95, 1 - s0),
                  A.point("glow_fuller", 0.95, 1 - s1), A.point("glow_fuller", 0.05, 1 - s1)]
            centre = (a0 + b0) / 2 - np.array([side * 0.01, 0, 0])
            _face(m, [a0, b0, b1, a1], uv, centre)


def handle_y0(d):
    """Bottom of the handle. The TOP stays at the Katana's (HANDLE_Y1), so the hands
    grip in the same place whatever the blade's size; a longer handle grows down."""
    return HANDLE_Y1 - d.get("handle_len", HANDLE_Y1 - HANDLE_Y0)


def build_hilt(B, d):
    """Collar, handle wrap and pommel (lathes round the y axis)."""
    s = 1.0
    hy0 = handle_y0(d)
    k = max(1.0, d["width"] / 0.030)          # a wider blade gets a wider collar
    # collar (habaki) at the blade base
    B.lathe([(0.0, 0.0), (0.0105, 0.0), (0.0115, 0.006), (0.0100, 0.016), (0.0, 0.016)], "accent",
            base=(0, GUARD_Y + 0.002, 0.0), nu=10, squash=(0.55 * k ** 0.5, 1.6 * k), scale=s)
    # handle
    hl = HANDLE_Y1 - hy0 - 0.006
    r = d.get("handle_r", 0.0125)
    B.lathe([(0.0, 0.0), (r, 0.0), (r * 1.08, hl * 0.38), (r * 1.02, hl * 0.86), (r * 0.98, hl), (0.0, hl)],
            "wrap", base=(0, hy0 + 0.004, 0.0), nu=12, squash=(0.8, 1.0), scale=s)


def build_guard(B, d):
    """The guard, in the x/z plane at GUARD_Y."""
    g = d["guard"]
    y = GUARD_Y
    if g == "crescent":
        # a thin gold disc with a crescent swept round the edge-side and a glowing eclipse gem
        B.lathe([(0.0, -0.003), (0.028, -0.003), (0.030, 0.0), (0.028, 0.003), (0.0, 0.003)], "guard",
                base=(0, y, 0.002), nu=24, squash=(0.75, 1.0))
        n = 13
        for i in range(n):
            a = -0.5 * math.pi + math.pi * i / (n - 1)          # half circle on the +z (edge) side
            r = 0.031 + 0.012 * math.sin(math.pi * i / (n - 1))
            thick = 0.0045 + 0.004 * math.sin(math.pi * i / (n - 1))
            B.ellipsoid((r * math.sin(a) * 0.75, y, r * math.cos(a) + 0.002), (thick, 0.004, thick), "guard", nu=8, nv=5)
        for side in (-1, 1):
            B.ellipsoid((side * 0.0185, y, -0.006), (0.0035, 0.0035, 0.0035), "glow_gem", nu=8, nv=6)
    elif g == "crystal":
        # ice crystals grown out of a frosted ring, swept up toward the blade, glowing at the core
        B.lathe([(0.0, -0.005), (0.026, -0.005), (0.029, 0.0), (0.026, 0.005), (0.0, 0.005)], "guard",
                base=(0, y, 0.0), nu=6, squash=(0.8, 1.15))
        spikes = [(0, 0.095, 0.30), (180, 0.095, 0.30), (35, 0.068, 0.55), (145, 0.068, 0.55), (-35, 0.068, 0.55),
                  (-145, 0.068, 0.55), (90, 0.055, 0.15), (-90, 0.055, 0.15)]
        for ang, L, up in spikes:
            a = math.radians(ang)
            dvec = np.array([0.55 * math.sin(a), up, math.cos(a)])    # z = along the edge, x = across the flat
            R = MW.align_y(dvec)
            B.lathe([(0.0, 0.0), (0.011, 0.0), (0.0085, L * 0.55), (0.0, L)], "guard",
                    base=tuple(np.array([0, y, 0]) + R @ np.array([0, 0.012, 0])), rot=R, nu=5, scale=1.0)
            B.lathe([(0.0, 0.0), (0.004, 0.0), (0.0, L * 0.45)], "glow_gem",
                    base=tuple(np.array([0, y, 0]) + R @ np.array([0, 0.012 + L * 0.5, 0])), rot=R, nu=5, scale=1.0)
        for side in (-1, 1):
            B.ellipsoid((side * 0.024, y, 0.0), (0.006, 0.009, 0.009), "glow_gem", nu=8, nv=6)
    else:
        GUARDS[g](B, d, y, guard_k(d))


def build_pommel(B, d):
    p = d["pommel"]
    y = handle_y0(d) + 0.004
    if p == "cap":
        B.lathe([(0.0, 0.0), (0.0128, 0.0), (0.0135, 0.004), (0.010, 0.010), (0.0, 0.011)], "accent",
                base=(0, y - 0.010, 0.0), nu=12, squash=(0.8, 1.0))
        B.ellipsoid((0, y - 0.0115, 0.0), (0.0035, 0.0025, 0.0035), "glow_gem", nu=8, nv=5)
    elif p == "crystal":
        B.lathe([(0.0, 0.0), (0.0135, 0.0), (0.014, 0.006), (0.0, 0.008)], "guard", base=(0, y - 0.006, 0.0), nu=6, squash=(0.8, 1.0))
        R = MW.align_y((0, -1, 0))
        B.lathe([(0.0, 0.0), (0.010, 0.0), (0.007, 0.018), (0.0, 0.034)], "guard", base=(0, y - 0.006, 0.0), rot=R, nu=5)
        B.lathe([(0.0, 0.0), (0.004, 0.0), (0.0, 0.018)], "glow_gem", base=(0, y - 0.020, 0.0), rot=R, nu=5)
    else:
        POMMELS[p](B, d, y)


# =========================================================================== the other 18 guards and pommels (0.6.0)
# Guards lie in the x/z plane at GUARD_Y (z = toward the cutting edge, x = across the
# flat, +y = toward the tip). Every size is in metres and scaled by guard_k(), which
# grows with the blade's width, so an oversized blade gets a matching guard.
def guard_k(d):
    return max(1.0, d["width"] / 0.034)


def _cone(B, base, direction, r, L, region, nu=6, push=0.0):
    """A cone from `base` along `direction`. push moves the base out along the direction
    (cones fanning out of one point must not share their base disc)."""
    R = MW.align_y(direction)
    base = np.asarray(base, dtype=float) + R @ np.array([0.0, push, 0.0])
    B.lathe([(0.0, 0.0), (r, 0.0), (r * 0.7, L * 0.5), (0.0, L)], region, base=tuple(base), rot=R, nu=nu)


def _disc(B, y, r, h, region, squash=(0.8, 1.0), nu=24, z=0.0):
    B.lathe([(0.0, -h), (r * 0.94, -h), (r, 0.0), (r * 0.94, h), (0.0, h)], region, base=(0, y, z), nu=nu, squash=squash)


def _ring(B, centre, R, r, region, axis=(0, 1, 0), nu=20, nv=8):
    """A torus round `axis`."""
    prof = [(R + r * math.cos(a), r * math.sin(a)) for a in [-math.pi / 2 + 2 * math.pi * i / (2 * nv) for i in range(2 * nv + 1)]]
    B.lathe(prof, region, base=tuple(centre), rot=MW.align_y(axis), nu=nu)


def _gem(B, pos, r, nu=8):
    B.ellipsoid(tuple(pos), (r, r, r), "glow_gem", nu=nu, nv=6)


def _petal(B, centre, direction, L, w, region, flat=0.35):
    R = MW.align_y(direction)
    c = np.asarray(centre, dtype=float) + R @ np.array([0, L * 0.5, 0])
    B.ellipsoid(tuple(c), (w, L * 0.5, w * flat), region, rot=R, nu=10, nv=6)


def _gems_both_faces(B, y, k, r=0.0045, z=0.0):
    for side in (-1, 1):
        _gem(B, (side * 0.012 * k, y, z), r * k)


def _horn(B, y, k, side, pts, rad, region_of):
    """A continuous curved horn: tapered cones from point to point with a ball at each
    joint, so the pieces always touch (no floating beads)."""
    P = [np.array([px * k, y + py * k, side * pz * k]) for px, py, pz in pts]
    for j, (a, b) in enumerate(zip(P[:-1], P[1:])):
        dv = b - a
        L = float(np.linalg.norm(dv))
        R = MW.align_y(dv / L)
        r0, r1 = rad[j] * k, rad[j + 1] * k
        B.lathe([(0.0, 0.0), (r0, 0.0), (r1, L), (0.0, L)], region_of(j), base=tuple(a), rot=R, nu=8)
        if j > 0:
            B.ellipsoid(tuple(a), (r0 * 1.02, r0 * 1.02, r0 * 1.02), region_of(j), nu=8, nv=5)


def g_blossom(B, d, y, k):          # Sakura Requiem: five rose-gold petals, glowing heart
    _disc(B, y, 0.018 * k, 0.004, "accent", nu=16)
    for i in range(5):
        a = TAU * i / 5 + math.pi / 2
        _petal(B, (0, y, 0), (0.75 * math.sin(a), 0.12, math.cos(a)), 0.040 * k, 0.017 * k, "guard")
    _gems_both_faces(B, y, k)


def g_moon(B, d, y, k):             # Void Crescent: a waning moon round the spine side
    _disc(B, y, 0.020 * k, 0.004, "guard", nu=16)
    n = 15
    for i in range(n):
        s = i / (n - 1)
        a = math.pi * 0.5 + math.pi * s          # half circle on the spine (-z) side
        r = 0.034 * k
        th = (0.004 + 0.008 * math.sin(math.pi * s)) * k
        B.ellipsoid((r * math.sin(a) * 0.8, y + 0.010 * k * math.sin(math.pi * s), r * math.cos(a)), (th, th * 0.8, th), "guard", nu=8, nv=5)
    _gem(B, (0, y + 0.006 * k, -0.036 * k), 0.008 * k)
    _gems_both_faces(B, y, k, 0.004)


def g_sunburst(B, d, y, k):         # Dawnbringer: twelve gold rays
    _disc(B, y, 0.024 * k, 0.005, "guard", nu=24)
    for i in range(12):
        a = TAU * i / 12
        L = (0.034 if i % 2 == 0 else 0.022) * k
        base = np.array([0.018 * k * math.sin(a) * 0.8, y, 0.018 * k * math.cos(a)])
        _cone(B, base, (0.8 * math.sin(a), 0.05, math.cos(a)), 0.0055 * k, L, "guard", nu=4)
    _gems_both_faces(B, y, k, 0.006)


def g_bolt(B, d, y, k):             # Stormcaller: an oval guard with two lightning prongs
    _disc(B, y, 0.024 * k, 0.005, "guard", squash=(0.7, 1.15), nu=20)
    for side in (-1, 1):
        pts = [(0, 0.00, 0.020), (0.006, 0.012, 0.034), (-0.004, 0.018, 0.044), (0.004, 0.034, 0.058)]
        P = [np.array([px * k, y + py * k, side * pz * k]) for px, py, pz in pts]
        for a, b in zip(P[:-1], P[1:]):
            B.m.bar(tuple(a), tuple(b), 0.007 * k, 0.005 * k, B.A.uv("accent"))
        _gem(B, P[-1], 0.004 * k)
    _gems_both_faces(B, y, k)


def g_fang(B, d, y, k):             # Emberfang: two curved black fangs reaching up the blade
    _disc(B, y, 0.020 * k, 0.005, "guard", squash=(0.75, 1.1), nu=16)
    for side in (-1, 1):
        pts = [(0.0, 0.0, 0.024), (0.0, 0.016, 0.034), (0.0, 0.034, 0.036), (0.0, 0.050, 0.030)]
        rad = [0.0075, 0.0060, 0.0042, 0.0022]
        _horn(B, y, k, side, pts, rad, lambda j: "guard")
        _gem(B, (0, y + 0.004 * k, side * 0.022 * k), 0.004 * k)
    _gems_both_faces(B, y, k)


def g_serpent(B, d, y, k):          # Serpent's Whisper: a serpent coiled once round the base
    n = 22
    for i in range(n):
        s = i / (n - 1)
        a = TAU * s * 1.1
        r = 0.022 * k
        th = (0.0065 - 0.003 * s) * k
        B.ellipsoid((r * math.sin(a) * 0.8, y + 0.012 * k * s, r * math.cos(a)), (th, th, th), "guard", nu=8, nv=5)
    hx, hz = 0.0, 0.026 * k
    B.ellipsoid((hx, y - 0.002 * k, hz + 0.008 * k), (0.009 * k, 0.006 * k, 0.012 * k), "guard", nu=10, nv=6)   # the head
    for side in (-1, 1):
        _gem(B, (side * 0.006 * k, y + 0.002 * k, hz + 0.012 * k), 0.0025 * k)                          # eyes
    _gems_both_faces(B, y, k, 0.004)


def g_star(B, d, y, k):             # Starfall: a four-point star
    _disc(B, y, 0.016 * k, 0.005, "guard", nu=12)
    for ang, L in ((0, 0.050), (180, 0.050), (90, 0.034), (-90, 0.034)):
        a = math.radians(ang)
        _cone(B, (0, y, 0), (0.8 * math.sin(a), 0.0, math.cos(a)), 0.012 * k, L * k, "guard", nu=4, push=0.006 * k)
    for ang in (45, 135, -45, -135):
        a = math.radians(ang)
        _cone(B, (0, y, 0), (0.8 * math.sin(a), 0.0, math.cos(a)), 0.006 * k, 0.020 * k, "accent", nu=4, push=0.008 * k)
    _gems_both_faces(B, y, k, 0.006)


def g_fullmoon(B, d, y, k):         # Bloodmoon: a full dark disc ringed in crimson
    _disc(B, y, 0.034 * k, 0.005, "guard", nu=28)
    _ring(B, (0, y, 0), 0.034 * k, 0.0035 * k, "accent", nu=28, nv=5)
    for i in range(6):
        a = TAU * i / 6
        _gem(B, (0.028 * k * math.sin(a) * 0.8, y + 0.004, 0.028 * k * math.cos(a)), 0.0028 * k)
    _gems_both_faces(B, y, k)


def g_square(B, d, y, k):           # Jade Phantom: a rounded square guard, jade at the corners
    B.lathe([(0.0, -0.005), (0.028 * k, -0.005), (0.030 * k, 0.0), (0.028 * k, 0.005), (0.0, 0.005)], "guard",
            base=(0, y, 0.0), rot=MW.rot_xyz(ry=45), nu=4, squash=(0.8, 1.0))
    for i in range(4):
        a = TAU * i / 4
        B.ellipsoid((0.024 * k * math.sin(a) * 0.8, y + 0.003, 0.024 * k * math.cos(a)), (0.005 * k, 0.004 * k, 0.005 * k), "accent", nu=8, nv=5)
    _gems_both_faces(B, y, k)


def g_wave(B, d, y, k):             # Sunken Relic: a worn disc with a scalloped wave rim, a sea pearl
    _disc(B, y, 0.028 * k, 0.005, "guard", nu=24)
    for i in range(14):
        a = TAU * i / 14
        B.ellipsoid((0.030 * k * math.sin(a) * 0.8, y + (0.004 if i % 2 else -0.002) * k, 0.030 * k * math.cos(a)),
                    (0.006 * k, 0.005 * k, 0.006 * k), "accent", nu=8, nv=5)
    _gems_both_faces(B, y, k, 0.006)


def g_wings(B, d, y, k):            # Dragon's Oath: two bronze wings of feathered plates
    _disc(B, y, 0.018 * k, 0.006, "guard", nu=16)
    for side in (-1, 1):
        for j, (L, up) in enumerate(((0.060, 0.10), (0.050, 0.35), (0.040, 0.60), (0.030, 0.85))):
            _petal(B, (0, y + 0.002 * j * k, side * 0.012 * k), (0.0, up, side * 1.0), L * k, 0.010 * k, "guard", flat=0.45)
    B.ellipsoid((0, y + 0.004 * k, 0), (0.012 * k, 0.010 * k, 0.012 * k), "accent", nu=10, nv=6)   # the dragon's head boss
    _gems_both_faces(B, y + 0.004 * k, k, 0.0045)


def g_flower(B, d, y, k):           # Moonflower: eight lavender petals in two rings
    for i in range(8):
        a = TAU * i / 8
        _petal(B, (0, y, 0), (0.75 * math.sin(a), 0.08, math.cos(a)), 0.036 * k, 0.013 * k, "guard")
    for i in range(8):
        a = TAU * i / 8 + TAU / 16
        _petal(B, (0, y + 0.003, 0), (0.75 * math.sin(a), 0.35, math.cos(a)), 0.024 * k, 0.010 * k, "accent")
    _gems_both_faces(B, y + 0.004, k)


def g_crown(B, d, y, k):            # Obsidian Crown: a silver ring with crown points up the blade
    _disc(B, y, 0.026 * k, 0.005, "dark", nu=20)
    _ring(B, (0, y, 0), 0.026 * k, 0.004 * k, "guard", nu=24, nv=5)
    for i in range(8):
        a = TAU * i / 8
        base = np.array([0.026 * k * math.sin(a) * 0.8, y, 0.026 * k * math.cos(a)])
        _cone(B, base, (0.25 * math.sin(a), 1.0, 0.25 * math.cos(a)), 0.0055 * k, (0.026 if i % 2 == 0 else 0.016) * k, "guard", nu=4)
        if i % 2 == 0:
            _gem(B, base + np.array([0, 0.004 * k, 0]), 0.0032 * k)
    _gems_both_faces(B, y, k)


def g_koi(B, d, y, k):              # Golden Koi: two gold koi fins sweeping back, red markings
    _disc(B, y, 0.018 * k, 0.005, "guard", nu=16)
    for side in (-1, 1):
        _petal(B, (0, y, side * 0.010 * k), (0.0, -0.25, side * 1.0), 0.058 * k, 0.020 * k, "guard", flat=0.25)
        _petal(B, (0, y + 0.002, side * 0.014 * k), (0.0, 0.25, side * 1.0), 0.034 * k, 0.012 * k, "accent", flat=0.3)
    _gems_both_faces(B, y, k)


def g_round(B, d, y, k):            # Spirit Lantern: a plain round guard with four small lights
    _disc(B, y, 0.026 * k, 0.006, "guard", nu=24)
    for i in range(4):
        a = TAU * i / 4 + TAU / 8
        _gem(B, (0.020 * k * math.sin(a) * 0.8, y + 0.0055, 0.020 * k * math.cos(a)), 0.003 * k)
    _gems_both_faces(B, y, k)


def g_horns(B, d, y, k):            # Thunder Oni: two horns curving up and out, red over black
    _disc(B, y, 0.020 * k, 0.006, "guard", squash=(0.75, 1.1), nu=16)
    for side in (-1, 1):
        pts = [(0.0, 0.000, 0.020), (0.0, 0.010, 0.036), (0.0, 0.026, 0.048), (0.0, 0.046, 0.052), (0.0, 0.062, 0.046)]
        rad = [0.0085, 0.0070, 0.0055, 0.0038, 0.0020]
        _horn(B, y, k, side, pts, rad, lambda j: "accent" if j >= 2 else "guard")
    _gems_both_faces(B, y, k)


def g_thread(B, d, y, k):           # Celestial Thread: a slim disc with two orbiting blue rings
    _disc(B, y, 0.022 * k, 0.004, "guard", nu=24)
    _ring(B, (0, y, 0), 0.030 * k, 0.0022 * k, "accent", axis=(0, 1, 0.35), nu=28, nv=4)
    _ring(B, (0, y, 0), 0.030 * k, 0.0022 * k, "accent", axis=(0, 1, -0.35), nu=28, nv=4)
    for i in range(6):
        a = TAU * i / 6
        _gem(B, (0.030 * k * math.sin(a) * 0.95, y + 0.0105 * k * math.cos(a), 0.030 * k * math.cos(a) * 0.95), 0.0022 * k)
    _gems_both_faces(B, y, k, 0.0035)


def g_chipped(B, d, y, k):          # Last Ember: a battered guard with a piece broken off
    B.lathe([(0.0, -0.006), (0.026 * k, -0.006), (0.028 * k, 0.0), (0.026 * k, 0.006), (0.0, 0.006)], "guard",
            base=(0.002, y, 0.004 * k), nu=7, squash=(0.8, 1.1))
    for (px, pz, r) in ((0.008, -0.020, 0.006), (-0.010, 0.022, 0.005), (0.012, 0.018, 0.004)):
        B.ellipsoid((px * k, y + 0.005, pz * k), (r * k, 0.003 * k, r * k), "dark", nu=8, nv=4)   # dents and scorch marks
    _gems_both_faces(B, y, k, 0.0045)


GUARDS = {"blossom": g_blossom, "moon": g_moon, "sunburst": g_sunburst, "bolt": g_bolt, "fang": g_fang,
          "serpent": g_serpent, "star": g_star, "fullmoon": g_fullmoon, "square": g_square, "wave": g_wave,
          "wings": g_wings, "flower": g_flower, "crown": g_crown, "koi": g_koi, "round": g_round,
          "horns": g_horns, "thread": g_thread, "chipped": g_chipped}


def _cap(B, y, region="accent", r=0.0135):
    B.lathe([(0.0, 0.0), (r, 0.0), (r * 1.05, 0.004), (r * 0.75, 0.010), (0.0, 0.011)], region, base=(0, y - 0.010, 0.0),
            nu=12, squash=(0.8, 1.0))


DOWN = (0, -1, 0)


def p_ring(B, d, y):
    _cap(B, y)
    _ring(B, (0, y - 0.024, 0), 0.012, 0.0035, "accent", axis=(1, 0, 0), nu=16, nv=5)
    _gem(B, (0, y - 0.024, 0), 0.0045)


def p_sun(B, d, y):
    _cap(B, y)
    for i in range(8):
        a = TAU * i / 8
        _cone(B, (0, y - 0.016, 0), (0.8 * math.sin(a), -0.3, math.cos(a)), 0.003, 0.014, "accent", nu=4, push=0.005)
    _gem(B, (0, y - 0.016, 0), 0.0065)


def p_fang(B, d, y):
    _cap(B, y, "guard")
    _cone(B, (0, y - 0.008, 0), DOWN, 0.008, 0.032, "guard", nu=6)
    _gem(B, (0, y - 0.012, 0), 0.004)


def p_gem(B, d, y):
    _cap(B, y)
    B.ellipsoid((0, y - 0.018, 0), (0.0085, 0.011, 0.0085), "glow_gem", nu=10, nv=8)


def p_star(B, d, y):
    _cap(B, y)
    for ang in (0, 90, 180, 270):
        a = math.radians(ang)
        _cone(B, (0, y - 0.018, 0), (0.8 * math.sin(a), 0.0, math.cos(a)), 0.004, 0.016, "accent", nu=4, push=0.004)
    _cone(B, (0, y - 0.018, 0), DOWN, 0.004, 0.016, "accent", nu=4, push=0.004)
    _gem(B, (0, y - 0.018, 0), 0.0055)


def p_shell(B, d, y):
    _cap(B, y)
    for i in range(5):
        a = -0.6 + 1.2 * i / 4
        _petal(B, (0, y - 0.008, 0), (0.0, -1.0, math.sin(a) * 1.4), 0.024, 0.006, "accent", flat=0.4)
    _gem(B, (0, y - 0.012, 0), 0.0045)


def p_claw(B, d, y):
    _cap(B, y, "guard")
    for i in range(3):
        a = TAU * i / 3
        _cone(B, (0.007 * math.sin(a), y - 0.010, 0.007 * math.cos(a)), (0.35 * math.sin(a), -1.0, 0.35 * math.cos(a)), 0.0035, 0.020, "guard", nu=5)
    _gem(B, (0, y - 0.020, 0), 0.0075)


def p_bud(B, d, y):
    _cap(B, y)
    B.lathe([(0.0, 0.0), (0.009, 0.006), (0.010, 0.014), (0.006, 0.024), (0.0, 0.030)], "guard",
            base=(0, y - 0.010, 0), rot=MW.align_y(DOWN), nu=10)
    _gem(B, (0, y - 0.022, 0), 0.0045)


def p_crown(B, d, y):
    _cap(B, y, "guard")
    for i in range(6):
        a = TAU * i / 6
        _cone(B, (0.010 * math.sin(a), y - 0.010, 0.010 * math.cos(a)), (0.2 * math.sin(a), -1.0, 0.2 * math.cos(a)), 0.0035, 0.016, "guard", nu=4)
    _gem(B, (0, y - 0.014, 0), 0.006)


def p_fin(B, d, y):
    _cap(B, y, "guard")
    for side in (-1, 1):
        _petal(B, (0, y - 0.010, 0), (0.0, -1.0, side * 0.9), 0.030, 0.010, "accent", flat=0.3)
    _gem(B, (0, y - 0.012, 0), 0.0045)


def p_lantern(B, d, y):             # Spirit Lantern: a small caged lantern, glowing inside
    top = y - 0.006
    B.lathe([(0.0, 0.0), (0.014, 0.0), (0.012, 0.005), (0.0, 0.006)], "accent", base=(0, top - 0.004, 0), nu=10)
    bottom = top - 0.040
    B.lathe([(0.0, 0.0), (0.014, 0.0), (0.012, 0.005), (0.0, 0.006)], "accent", base=(0, bottom, 0), nu=10)
    for i in range(4):
        a = TAU * i / 4 + TAU / 8
        x, z = 0.011 * math.sin(a), 0.011 * math.cos(a)
        B.m.bar((x, bottom + 0.004, z), (x, top - 0.003, z), 0.0025, 0.0025, B.A.uv("accent"))
    B.ellipsoid((0, (top + bottom) / 2, 0), (0.0085, 0.015, 0.0085), "glow_gem", nu=10, nv=8)
    _ring(B, (0, bottom - 0.008, 0), 0.006, 0.0018, "accent", axis=(1, 0, 0), nu=12, nv=4)


POMMELS = {"ring": p_ring, "sun": p_sun, "fang": p_fang, "gem": p_gem, "star": p_star, "shell": p_shell,
           "claw": p_claw, "bud": p_bud, "crown": p_crown, "fin": p_fin, "lantern": p_lantern}


def build(key):
    """(mesh, atlas) of one blade in the Katana's frame."""
    d = BY_KEY[key]
    A = make_atlas(d)
    m = core.Mesh()
    build_blade(m, A, d)
    B = K.Builder(A)
    build_hilt(B, d)
    build_guard(B, d)
    build_pommel(B, d)
    m.merge(B.m)
    return m.check(item_id(key)), A


# =========================================================================== pictures (icons, stickers, inspect)
def lit_and_glow(m, A, yaw, pitch, size, ss=3, fit=0.9, frame=None, outline=None):
    """Render like the game: normal texels lit, glow texels at full brightness,
    plus a soft bloom around the glow (pictures only; the game has no bloom)."""
    im = K.render(m, A.img, yaw=yaw, pitch=pitch, size=size, ss=ss, fit=fit, frame=frame, outline=outline, emissive_u=GLOW_U)
    mask_tex = A.img.copy()
    dm = ImageDraw.Draw(mask_tex)
    dm.rectangle([0, 0, int(SIZE * GLOW_U) - 1, SIZE], fill=(0, 0, 0, 255))
    gl = K.render(m, mask_tex, yaw=yaw, pitch=pitch, size=size, ss=ss, fit=fit, frame=frame, emissive_u=GLOW_U)
    a = np.asarray(gl).astype(np.float32)
    lum = a[..., :3].max(-1) / 255.0 * (a[..., 3] / 255.0)
    rgb = a[..., :3]
    halo = Image.fromarray(np.dstack([rgb, np.clip(lum * 255 * 1.6, 0, 255)]).astype(np.uint8), "RGBA").filter(ImageFilter.GaussianBlur(size * 0.025))
    halo2 = Image.fromarray(np.dstack([rgb, np.clip(lum * 255 * 1.6, 0, 255)]).astype(np.uint8), "RGBA").filter(ImageFilter.GaussianBlur(size * 0.06))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.alpha_composite(halo2)
    out.alpha_composite(halo)
    out.alpha_composite(im)
    return out


def icon(m, A):
    """32x32 inventory icon: the sword on the diagonal, glowing."""
    import copy
    R = core._rot("z", -45) @ core._rot("y", 90)   # the flat of the blade toward the viewer, on the diagonal
    mm = copy.copy(m)
    mm.v = [R @ np.asarray(v) for v in m.v]
    mm.n = [R @ np.asarray(n) for n in m.n]
    im = lit_and_glow(mm, A, yaw=0, pitch=0, size=128, fit=0.98, outline=(30, 24, 40))
    return im.resize((32, 32), Image.LANCZOS)


def turntable(m, A, frames=16, size=320, pitch=14, fit=0.84, yaw0=-22):
    V = np.array(m.v)
    yaws = [yaw0 + i * 360.0 / frames for i in range(frames)]
    lo = np.array([1e9, 1e9])
    hi = -lo
    for yv in yaws:
        R = core._rot("x", pitch) @ core._rot("y", -yv)
        P = (V @ R.T)[:, :2]
        lo = np.minimum(lo, P.min(0))
        hi = np.maximum(hi, P.max(0))
    span = max(hi[0] - lo[0], hi[1] - lo[1]) / fit
    frame = ((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, span)
    return [lit_and_glow(m, A, yaw=yv, pitch=pitch, size=size, ss=2, frame=frame) for yv in yaws]
