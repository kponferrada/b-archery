"""Jamie's Treasures - Treasured Crossbows (0.11.0): 10 original glowing crossbows.

Built in the SAME frame as the game's own Hunting Rifle mesh
(media/models_X/weapons/firearm/MSR788_Rifle.x, read from the 42.21 install):
    origin = where the right hand holds (pistol grip), +Y = forward (muzzle at
    y ~0.50), +Z = up (scope at z ~0.05), X = sideways, metres.
so the Hunting Rifle's own hand / world attachment points (copied into each model
script) hold, aim and drop it like the rifle.

Texture: one 512 x 512 per crossbow in the Treasured Blades' layout (blades.GlowAtlas):
    u <  0.734  normal texels (lit by the scene)
    u >= 0.766  GLOW texels (full brightness through the existing jc_glow shader)
so the glow is on the model itself: in the hands, aiming, firing, on the back and on
the floor. It is surface glow (emissive texels), not a light: the 42.21 model shader
path has no per-model light source, and an IsoLightSource per crossbow would cost a
light update every time one moves (see docs/CROSSBOWS.md).

All designs are original (Jamie's brief); none copies a weapon from a game, anime or film.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import core
import kawaii as K
import blades as BL
from statues import tube

TAU = 2 * math.pi
SIZE = BL.SIZE
GLOW_U = BL.GLOW_U

# =========================================================================== the 10 designs
# body / body2: main colours; metal: rail and fittings; accent: trim; glow: glow colour
# limbs: "recurve" | "compound" | "straight" | "forward" | "deflex"
# stock: "skeleton" | "wood" | "thumbhole" | "heavy" | "ornate"
DESIGNS = [
    dict(key="SilentReaper", name="Silent Reaper", rarity="Legendary",
         lore="A matte-black tactical crossbow with crimson accents. It makes almost no sound.",
         body=(34, 34, 38), body2=(24, 24, 28), metal=(70, 72, 78), accent=(150, 22, 34), string=(36, 36, 40),
         glow=(235, 30, 52), limbs="recurve", stock="skeleton", sight="reddot"),
    dict(key="Frostbite", name="Frostbite", rarity="Legendary",
         lore="Silver and icy blue, with frost grown along its limbs.",
         body=(176, 190, 206), body2=(120, 140, 166), metal=(200, 210, 222), accent=(110, 170, 220), string=(220, 230, 240),
         glow=(110, 200, 255), limbs="forward", stock="thumbhole", sight="crystal"),
    dict(key="VerdantStalker", wood=True, name="Verdant Stalker", rarity="Legendary",
         lore="A forest-green hunting crossbow with a walnut stock.",
         body=(52, 92, 56), body2=(110, 72, 40), metal=(90, 96, 88), accent=(60, 130, 70), string=(70, 60, 40),
         glow=(40, 230, 120), limbs="straight", stock="wood", sight="peep"),
    dict(key="Stormbreaker", name="Stormbreaker", rarity="Legendary",
         lore="Heavy dark steel with electric-blue lines that crackle along it.",
         body=(54, 58, 66), body2=(36, 38, 44), metal=(90, 96, 108), accent=(60, 120, 220), string=(40, 44, 52),
         glow=(90, 170, 255), limbs="compound", stock="heavy", sight="scope"),
    dict(key="GoldenViper", name="Golden Viper", rarity="Legendary",
         lore="Black and gold, with a serpent coiled along the rail.",
         body=(30, 28, 30), body2=(20, 18, 20), metal=(212, 170, 70), accent=(232, 186, 70), string=(60, 50, 30),
         glow=(255, 196, 70), limbs="recurve", stock="ornate", sight="serpent"),
    dict(key="Emberfall", wood=True, name="Emberfall", rarity="Legendary",
         lore="A dark wooden stock, bronze fittings and an edge of ember orange.",
         body=(70, 44, 30), body2=(50, 32, 22), metal=(176, 120, 64), accent=(200, 90, 30), string=(50, 40, 30),
         glow=(255, 120, 30), limbs="deflex", stock="wood", sight="peep"),
    dict(key="Moonshadow", name="Moonshadow", rarity="Legendary",
         lore="Midnight purple and silver, its limbs shaped like a crescent moon.",
         body=(44, 30, 70), body2=(28, 20, 46), metal=(196, 200, 214), accent=(170, 150, 220), string=(200, 200, 214),
         glow=(170, 90, 255), limbs="forward", stock="thumbhole", sight="moon"),
    dict(key="IronwoodSentinel", wood=True, name="Ironwood Sentinel", rarity="Legendary",
         lore="Rugged ironwood bound in riveted steel. Built to last.",
         body=(110, 80, 52), body2=(80, 58, 38), metal=(96, 98, 102), accent=(140, 110, 60), string=(60, 54, 44),
         glow=(255, 176, 60), limbs="straight", stock="heavy", sight="peep"),
    dict(key="JadePhantom", name="Jade Phantom", rarity="Legendary",
         lore="A dark-green body with jade inlays that glow like a ghost light.",
         body=(30, 52, 42), body2=(20, 36, 30), metal=(60, 70, 66), accent=(70, 170, 120), string=(30, 44, 38),
         glow=(60, 220, 150), limbs="deflex", stock="skeleton", sight="reddot"),
    dict(key="ObsidianCrown", name="Obsidian Crown", rarity="Legendary",
         lore="Black and silver, crowned with ornate silver fittings.",
         body=(24, 22, 28), body2=(16, 14, 20), metal=(200, 204, 214), accent=(200, 204, 214), string=(180, 182, 196),
         glow=(130, 40, 220), limbs="compound", stock="ornate", sight="crown"),
]
BY_KEY = {d["key"]: d for d in DESIGNS}


def item_id(key):
    return "JC_Crossbow_" + key


BOLT_ID = "JC_CrossbowBolt"


# =========================================================================== textures
def _mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def matte(c, w=64, h=64, seed=1, speck=0.06):
    """A matte surface: a soft vertical shade with fine grain (no shine)."""
    rng = np.random.default_rng(seed)
    y = np.linspace(1.08, 0.90, h)[:, None, None]
    base = np.array(c, dtype=float)[None, None, :] * y * np.ones((1, w, 1))
    base += rng.normal(0, 255 * speck * 0.25, (h, w, 1))
    a = np.clip(base, 0, 255).astype(np.uint8)
    return Image.fromarray(np.dstack([a, np.full((h, w), 255, np.uint8)]), "RGBA")


def wood(c, w=64, h=128, seed=3):
    im = matte(c, w, h, seed, speck=0.03)
    dr = ImageDraw.Draw(im)
    rng = np.random.default_rng(seed)
    for _ in range(14):
        x = rng.uniform(0, w)
        pts = [(x + 2.5 * math.sin(y / 9.0 + x), y) for y in range(0, h + 1, 4)]
        dr.line(pts, fill=_mix(c, (0, 0, 0), 0.35) + (255,), width=1)
    return im


def grip_tex(c, w=48, h=48):
    im = matte(c, w, h, 7)
    dr = ImageDraw.Draw(im)
    for y in range(2, h, 4):
        for x in range(2 + (y // 4) % 2 * 2, w, 4):
            dr.point((x, y), fill=_mix(c, (0, 0, 0), 0.5) + (255,))
    return im


def glow_tex(c, w=32, h=64):
    """Bright glow with a lighter core line, so a glowing strip reads as light."""
    im = Image.new("RGBA", (w, h), c + (255,))
    dr = ImageDraw.Draw(im)
    dr.rectangle([w * 0.35, 0, w * 0.65, h], fill=_mix(c, (255, 255, 255), 0.45) + (255,))
    return im


def make_atlas(d):
    A = BL.GlowAtlas(background=d["body"] + (255,))
    stock_tex = wood(d["body2"]) if d.get("wood") else matte(d["body2"], 64, 128, 4)
    A.add("body", matte(d["body"], 64, 128, 2))
    A.add("stock", stock_tex)
    A.add("metal", matte(d["metal"], 64, 64, 5, speck=0.03))
    A.add("accent", matte(d["accent"], 32, 32, 6, speck=0.03))
    A.add("grip", grip_tex(_mix(d["body"], (0, 0, 0), 0.3)))
    A.add("string", matte(d["string"], 16, 64, 8, speck=0.02))
    A.add("glow", glow_tex(d["glow"]), glow=True)
    A.add("glow_lens", glow_tex(_mix(d["glow"], (255, 255, 255), 0.25), 16, 16), glow=True)
    return A.finish()


# =========================================================================== geometry helpers
def _box(B, x0, x1, y0, y1, z0, z1, region):
    uv = B.A.uv(region)
    B.m.box(x0, x1, y0, y1, z0, z1, uv, bottom=uv)


def _sym_tube(B, pts, radii, region, side=(0, 1, 0), depth=1.0, nu=10, nv=None):
    """The same tube on both sides (x -> -x)."""
    for s in (1, -1):
        tube(B, [(s * p[0], p[1], p[2]) for p in pts], radii, region, nu=nu, nv=nv, side=side, depth=depth)


# =========================================================================== parts
def stock_skeleton(B, d):
    """Open tactical stock: two rails to a butt plate, a crimson-lit plate edge."""
    _box(B, -0.017, 0.017, -0.215, -0.198, -0.080, 0.022, "body")                       # butt plate
    _box(B, -0.0175, 0.0175, -0.209, -0.202, -0.066, 0.008, "glow")                     # glowing plate edge
    tube(B, [(0, -0.200, 0.012), (0, -0.10, 0.012), (0, -0.01, 0.014)], [0.0085, 0.0085, 0.0085], "body", nu=10)
    tube(B, [(0, -0.200, -0.068), (0, -0.12, -0.050), (0, -0.05, -0.028), (0, -0.015, -0.012)],
         [0.0075, 0.0075, 0.0075, 0.0075], "body", nu=10)
    tube(B, [(0, -0.125, -0.050), (0, -0.115, -0.010), (0, -0.110, 0.010)], [0.005, 0.005, 0.005], "accent", nu=8)  # strut
    _box(B, -0.010, 0.010, -0.150, -0.120, 0.014, 0.030, "grip")                        # cheek rest


def grip(B, d):
    tube(B, [(0, 0.004, -0.004), (0, -0.012, -0.050), (0, -0.026, -0.098)], [0.0125, 0.0130, 0.0120], "grip", nu=12,
         side=(1, 0, 0), depth=0.75)
    tube(B, [(0, 0.004, -0.022), (0, 0.030, -0.048), (0, 0.052, -0.040), (0, 0.056, -0.014)], [0.0032] * 4, "metal", nu=8)
    tube(B, [(0, 0.024, -0.012), (0, 0.030, -0.032)], [0.0028, 0.0022], "accent", nu=6)   # trigger


def receiver(B, d):
    _box(B, -0.021, 0.021, -0.012, 0.215, -0.022, 0.030, "body")
    _box(B, -0.017, 0.017, 0.215, 0.375, -0.030, 0.028, "body")                         # fore-end
    _box(B, -0.012, 0.012, -0.005, 0.440, 0.030, 0.044, "metal")                        # rail / flight groove
    _box(B, 0.0120, 0.0135, 0.050, 0.400, 0.033, 0.041, "glow")                         # glowing inlays on the rail sides
    _box(B, -0.0135, -0.0120, 0.050, 0.400, 0.033, 0.041, "glow")
    _box(B, -0.0215, 0.0215, 0.100, 0.180, 0.004, 0.012, "accent")                      # trim band
    _box(B, -0.010, 0.010, 0.120, 0.150, 0.044, 0.052, "metal")                         # latch housing


def prod_mount(B, d):
    _box(B, -0.032, 0.032, 0.372, 0.420, -0.012, 0.040, "metal")
    _box(B, -0.033, 0.033, 0.392, 0.402, -0.006, 0.034, "accent")


LIMB_Y, LIMB_Z = 0.398, 0.016


def limbs_recurve(B, d):
    """Recurve limbs swept back, tips turning forward again; a glowing edge on each."""
    pts = [(0.032, LIMB_Y, LIMB_Z), (0.11, LIMB_Y - 0.010, LIMB_Z), (0.19, LIMB_Y - 0.032, LIMB_Z),
           (0.245, LIMB_Y - 0.050, LIMB_Z), (0.272, LIMB_Y - 0.040, LIMB_Z), (0.284, LIMB_Y - 0.018, LIMB_Z)]
    _sym_tube(B, pts, [0.013, 0.012, 0.010, 0.0085, 0.0070, 0.0055], "body", side=(0, 1, 0), depth=0.42, nu=12, nv=26)
    glow = [(p[0], p[1] + 0.008, p[2] + 0.0035) for p in pts[:-1]]
    _sym_tube(B, glow, [0.0030, 0.0030, 0.0028, 0.0024, 0.0020], "glow", side=(0, 1, 0), depth=0.7, nu=8, nv=22)
    for s in (1, -1):
        B.ellipsoid((s * 0.284, LIMB_Y - 0.018, LIMB_Z), (0.006, 0.006, 0.006), "accent", nu=10, nv=6)
    return [(0.282, LIMB_Y - 0.022, LIMB_Z)]


LIMBS = {"recurve": limbs_recurve}   # the others are added below (after their definitions)


def string(B, tip, latch=(0.0, 0.132, 0.046)):
    x, y, z = tip
    for s in (1, -1):
        tube(B, [(s * x, y, z), (s * x * 0.5, (y + latch[1]) / 2, (z + latch[2]) / 2), latch], [0.0016] * 3, "string", nu=6,
             caps=False)


def stirrup(B, d):
    tube(B, [(-0.028, 0.418, 0.000), (-0.036, 0.452, 0.000), (-0.020, 0.482, 0.000), (0.0, 0.488, 0.000),
             (0.020, 0.482, 0.000), (0.036, 0.452, 0.000), (0.028, 0.418, 0.000)], [0.0045] * 7, "metal", nu=8, nv=30)


def sight_reddot(B, d):
    _box(B, -0.011, 0.011, 0.060, 0.104, 0.044, 0.056, "metal")
    tube(B, [(0, 0.064, 0.068), (0, 0.100, 0.068)], [0.012, 0.012], "body", nu=14)
    B.ellipsoid((0, 0.101, 0.068), (0.0085, 0.0015, 0.0085), "glow_lens", nu=12, nv=6)


# ---------------------------------------------------------------------------- more stocks (0.11.3)
def stock_thumbhole(B, d):
    """A solid sculpted stock with a thumbhole, a glowing line along the comb."""
    _box(B, -0.018, 0.018, -0.220, -0.196, -0.085, 0.026, "stock")                      # butt
    _box(B, -0.014, 0.014, -0.198, -0.020, 0.000, 0.028, "stock")                       # comb bar
    _box(B, -0.014, 0.014, -0.198, -0.070, -0.078, -0.048, "stock")                     # lower bar
    _box(B, -0.014, 0.014, -0.072, -0.040, -0.062, 0.002, "stock")                      # front post (the hole is between)
    _box(B, -0.0145, 0.0145, -0.190, -0.030, 0.026, 0.030, "glow")                      # glowing comb line
    _box(B, -0.0185, 0.0185, -0.222, -0.218, -0.080, 0.020, "accent")                   # butt pad


def stock_wood(B, d):
    """A classic shaped wooden stock, deep at the butt, slim at the wrist."""
    tube(B, [(0, -0.215, -0.028), (0, -0.150, -0.024), (0, -0.080, -0.016), (0, -0.020, -0.006)],
         [0.050, 0.044, 0.032, 0.020], "stock", nu=14, side=(0, 0, 1), depth=0.36)
    _box(B, -0.019, 0.019, -0.224, -0.214, -0.076, 0.020, "accent")                     # butt plate
    _box(B, -0.0185, 0.0185, -0.150, -0.140, -0.050, 0.012, "glow")                     # glowing band


def stock_heavy(B, d):
    """A heavy stock: the wooden shape, thicker, with a steel butt plate and two bands."""
    tube(B, [(0, -0.220, -0.030), (0, -0.150, -0.026), (0, -0.080, -0.018), (0, -0.020, -0.006)],
         [0.056, 0.050, 0.038, 0.024], "stock", nu=14, side=(0, 0, 1), depth=0.44)
    _box(B, -0.026, 0.026, -0.232, -0.220, -0.086, 0.026, "metal")
    for y in (-0.170, -0.100):
        tube(B, [(-0.026, y, -0.040), (0, y, -0.052), (0.026, y, -0.040), (0.026, y, 0.012), (0, y, 0.020), (-0.026, y, 0.012),
                 (-0.026, y, -0.040)], [0.004] * 7, "metal", nu=6, nv=28, caps=False)
    _box(B, -0.0262, 0.0262, -0.136, -0.126, -0.036, 0.008, "glow")


def stock_ornate(B, d):
    """A slim stock with gold (or silver) filigree along both sides and an ornament on the butt."""
    tube(B, [(0, -0.212, -0.024), (0, -0.140, -0.020), (0, -0.070, -0.014), (0, -0.016, -0.006)],
         [0.046, 0.040, 0.028, 0.018], "stock", nu=14, side=(0, 0, 1), depth=0.36)
    for s in (1, -1):
        tube(B, [(s * 0.0175, -0.200, -0.040), (s * 0.0172, -0.170, -0.010), (s * 0.0168, -0.140, -0.040),
                 (s * 0.0160, -0.110, -0.012), (s * 0.0150, -0.080, -0.030), (s * 0.0130, -0.040, -0.010)],
             [0.0022] * 6, "accent", nu=6, nv=30)
        B.ellipsoid((s * 0.0172, -0.170, -0.026), (0.0030, 0.0060, 0.0060), "glow_lens", nu=8, nv=6)
    _box(B, -0.018, 0.018, -0.222, -0.212, -0.070, 0.018, "accent")
    B.ellipsoid((0, -0.226, -0.026), (0.010, 0.006, 0.010), "glow_lens", nu=10, nv=6)


# ---------------------------------------------------------------------------- more limbs (0.11.3)
def _limb_pair(B, pts, radii, tip_r=0.006, glow_offset=0.008, cap="accent"):
    _sym_tube(B, pts, radii, "body", side=(0, 1, 0), depth=0.42, nu=12, nv=26)
    glow = [(p[0], p[1] + glow_offset, p[2] + 0.0035) for p in pts[:-1]]
    _sym_tube(B, glow, [min(0.0030, r * 0.3) for r in radii[:-1]], "glow", side=(0, 1, 0), depth=0.7, nu=8, nv=22)
    x, y, z = pts[-1]
    for s in (1, -1):
        B.ellipsoid((s * x, y, z), (tip_r, tip_r, tip_r), cap, nu=10, nv=6)
    return [(x - 0.002, y, z)]


def limbs_forward(B, d):
    """Limbs reaching FORWARD from the prod, tips curling back: a crescent seen from above."""
    pts = [(0.032, LIMB_Y, LIMB_Z), (0.11, LIMB_Y + 0.018, LIMB_Z), (0.18, LIMB_Y + 0.040, LIMB_Z),
           (0.235, LIMB_Y + 0.052, LIMB_Z), (0.268, LIMB_Y + 0.040, LIMB_Z), (0.280, LIMB_Y + 0.018, LIMB_Z)]
    return _limb_pair(B, pts, [0.013, 0.012, 0.010, 0.0085, 0.0070, 0.0055], glow_offset=-0.008)


def limbs_straight(B, d):
    """Plain, strong limbs swept straight back, broad at the root."""
    pts = [(0.032, LIMB_Y, LIMB_Z), (0.10, LIMB_Y - 0.010, LIMB_Z), (0.17, LIMB_Y - 0.020, LIMB_Z),
           (0.24, LIMB_Y - 0.030, LIMB_Z), (0.268, LIMB_Y - 0.034, LIMB_Z)]
    return _limb_pair(B, pts, [0.015, 0.013, 0.011, 0.0085, 0.0065], tip_r=0.0065)


def limbs_compound(B, d):
    """Short stiff limbs ending in cam wheels, a second cable between the cams."""
    pts = [(0.032, LIMB_Y, LIMB_Z), (0.08, LIMB_Y - 0.008, LIMB_Z), (0.13, LIMB_Y - 0.018, LIMB_Z), (0.165, LIMB_Y - 0.026, LIMB_Z)]
    _sym_tube(B, pts, [0.016, 0.014, 0.012, 0.010], "body", side=(0, 1, 0), depth=0.5, nu=12, nv=20)
    _sym_tube(B, [(p[0], p[1] + 0.009, p[2] + 0.004) for p in pts[:-1]], [0.003, 0.003, 0.0026], "glow", side=(0, 1, 0),
              depth=0.7, nu=8, nv=16)
    cx, cy = 0.180, LIMB_Y - 0.030
    for s in (1, -1):
        B.ellipsoid((s * cx, cy, LIMB_Z), (0.022, 0.022, 0.006), "metal", nu=16, nv=6)
        B.ellipsoid((s * cx, cy, LIMB_Z + 0.0065), (0.010, 0.010, 0.002), "glow_lens", nu=12, nv=4)
    tube(B, [(-cx, cy + 0.018, LIMB_Z), (0, cy + 0.024, LIMB_Z), (cx, cy + 0.018, LIMB_Z)], [0.0014] * 3, "string", nu=6,
         caps=False)
    return [(cx, cy - 0.020, LIMB_Z)]


def limbs_deflex(B, d):
    """Deflex limbs: first bending forward from the riser, then sweeping back to the tips."""
    pts = [(0.032, LIMB_Y, LIMB_Z), (0.08, LIMB_Y + 0.024, LIMB_Z), (0.15, LIMB_Y + 0.022, LIMB_Z),
           (0.215, LIMB_Y - 0.004, LIMB_Z), (0.260, LIMB_Y - 0.038, LIMB_Z), (0.274, LIMB_Y - 0.056, LIMB_Z)]
    return _limb_pair(B, pts, [0.013, 0.012, 0.0105, 0.009, 0.0072, 0.0058])


# ---------------------------------------------------------------------------- more sights (0.11.3)
def sight_crystal(B, d):
    _box(B, -0.008, 0.008, 0.070, 0.100, 0.044, 0.054, "metal")
    for k, (x, h) in enumerate(((0.0, 0.030), (-0.007, 0.020), (0.008, 0.018))):
        tube(B, [(x, 0.085, 0.054), (x * 1.3, 0.085, 0.054 + h * 0.6), (x * 1.6, 0.085, 0.054 + h)], [0.006, 0.004, 0.0004],
             "glow_lens" if k == 0 else "accent", nu=6, nv=6)


def sight_peep(B, d):
    tube(B, [(-0.010, 0.020, 0.050), (-0.010, 0.020, 0.072), (0, 0.020, 0.080), (0.010, 0.020, 0.072), (0.010, 0.020, 0.050)],
         [0.0028] * 5, "metal", nu=6, nv=16, caps=False)
    tube(B, [(0, 0.395, 0.044), (0, 0.395, 0.066)], [0.0025, 0.0020], "metal", nu=6)
    B.ellipsoid((0, 0.395, 0.068), (0.0035, 0.0035, 0.0035), "glow_lens", nu=8, nv=6)


def sight_scope(B, d):
    for y in (0.070, 0.150):
        _box(B, -0.008, 0.008, y - 0.008, y + 0.008, 0.044, 0.062, "metal")
    tube(B, [(0, 0.040, 0.074), (0, 0.110, 0.074), (0, 0.190, 0.074)], [0.016, 0.013, 0.017], "body", nu=16)
    B.ellipsoid((0, 0.191, 0.074), (0.0130, 0.0018, 0.0130), "glow_lens", nu=12, nv=6)
    B.ellipsoid((0, 0.039, 0.074), (0.0110, 0.0018, 0.0110), "glow_lens", nu=12, nv=6)
    _box(B, -0.0162, 0.0162, 0.104, 0.116, 0.060, 0.088, "accent")


def sight_serpent(B, d):
    """A gold serpent winding along the rail, head raised at the front, glowing eyes."""
    pts = []
    for k in range(13):
        t = k / 12.0
        pts.append((0.018 * math.sin(t * TAU * 1.5), 0.04 + 0.34 * t, 0.048 + 0.004 * math.cos(t * TAU * 1.5)))
    pts.append((0.0, 0.392, 0.066))
    tube(B, pts, [0.0035] * 13 + [0.006], "accent", nu=8, nv=60)
    for s in (1, -1):
        B.ellipsoid((s * 0.004, 0.396, 0.070), (0.0018, 0.0018, 0.0018), "glow_lens", nu=6, nv=4)
    sight_reddot(B, d)


def sight_moon(B, d):
    """A silver crescent sight with a glowing inner edge."""
    _box(B, -0.008, 0.008, 0.075, 0.105, 0.044, 0.052, "metal")
    arc = [(0.028 * math.cos(a), 0.090, 0.078 + 0.028 * math.sin(a)) for a in np.linspace(-1.9, 1.9, 9)]
    tube(B, arc, [0.0025, 0.004, 0.0055, 0.0065, 0.007, 0.0065, 0.0055, 0.004, 0.0025], "metal", nu=8, nv=30)
    inner = [(0.022 * math.cos(a), 0.0905, 0.078 + 0.022 * math.sin(a)) for a in np.linspace(-1.5, 1.5, 7)]
    tube(B, inner, [0.0015] * 7, "glow_lens", nu=6, nv=24)


def sight_crown(B, d):
    """A small silver crown on the rail with a glowing jewel, the same crown on the butt."""
    for y, z in ((0.090, 0.050), (-0.226, 0.030)):
        ring = [(0.014 * math.cos(a), y + 0.014 * math.sin(a), z) for a in np.linspace(0, TAU, 13)]
        tube(B, ring, [0.0025] * 13, "accent", nu=6, nv=36, caps=False)
        for k in range(5):
            a = TAU * k / 5
            base = (0.014 * math.cos(a), y + 0.014 * math.sin(a), z)
            tube(B, [base, (base[0] * 1.05, base[1], z + 0.012), (base[0] * 1.1, base[1], z + 0.018)], [0.0028, 0.0018, 0.0004],
                 "accent", nu=6, nv=6)
        B.ellipsoid((0, y, z + 0.008), (0.0055, 0.0055, 0.0055), "glow_lens", nu=10, nv=6)


# ---------------------------------------------------------------------------- per-design details (0.11.3)
def extra_frost(B, d):           # Frostbite: frost crystals at the limb roots
    for s in (1, -1):
        for k, (dx, dz, h) in enumerate(((0.040, 0.012, 0.026), (0.052, -0.006, 0.020), (0.064, 0.010, 0.016))):
            b = (s * dx, LIMB_Y + 0.004, LIMB_Z + dz * 0.3)
            tube(B, [b, (b[0] + s * 0.004, b[1] + 0.006, b[2] + h * 0.6), (b[0] + s * 0.006, b[1] + 0.008, b[2] + h)],
                 [0.0045, 0.003, 0.0004], "glow_lens" if k == 0 else "accent", nu=6, nv=6)


def extra_leaves(B, d):          # Verdant Stalker: carved leaves on the fore-end, glowing veins
    for s in (1, -1):
        for y in (0.250, 0.300, 0.345):
            c = (s * 0.0172, y, 0.004)
            B.ellipsoid(c, (0.0016, 0.016, 0.008), "accent", rot=core._rot("x", 25), nu=10, nv=6)
            tube(B, [(c[0] + s * 0.0016, y - 0.012, 0.0), (c[0] + s * 0.0016, y + 0.012, 0.008)], [0.0008, 0.0008], "glow_lens",
                 nu=4, nv=4)


def extra_lightning(B, d):       # Stormbreaker: lightning zigzags along the fore-end
    for s in (1, -1):
        zz = [(s * 0.0175, 0.220 + 0.020 * k, (-0.010 if k % 2 else 0.012)) for k in range(8)]
        tube(B, zz, [0.0016] * 8, "glow", nu=5, nv=40)


def extra_embers(B, d):          # Emberfall: glowing ember cracks on the stock
    rng = np.random.default_rng(17)
    for s in (1, -1):
        for _ in range(4):
            y0 = rng.uniform(-0.19, -0.06)
            z0 = rng.uniform(-0.035, 0.0)
            pts = [(s * 0.0175, y0 + 0.008 * k, z0 + rng.uniform(-0.006, 0.006)) for k in range(4)]
            tube(B, pts, [0.0012] * 4, "glow", nu=4, nv=12)


def extra_crescents(B, d):       # Moonshadow: crescent ornaments on the limb tips
    for s in (1, -1):
        c = (s * 0.282, LIMB_Y + 0.020, LIMB_Z + 0.010)
        arc = [(c[0] + 0.012 * math.cos(a) * s, c[1] + 0.012 * math.sin(a), c[2]) for a in np.linspace(-2.0, 2.0, 7)]
        tube(B, arc, [0.0015, 0.0028, 0.0036, 0.004, 0.0036, 0.0028, 0.0015], "metal", nu=6, nv=20)


def extra_rivets(B, d):          # Ironwood Sentinel: steel straps and rivets
    for y in (0.230, 0.330):
        _box(B, -0.0185, 0.0185, y, y + 0.012, -0.032, 0.030, "metal")
        for s in (1, -1):
            for z in (-0.020, 0.018):
                B.ellipsoid((s * 0.0190, y + 0.006, z), (0.0018, 0.0025, 0.0025), "accent", nu=6, nv=4)
    for s in (1, -1):
        for y in (-0.180, -0.120, -0.060):
            B.ellipsoid((s * 0.022, y, -0.012), (0.0018, 0.0025, 0.0025), "accent", nu=6, nv=4)


def extra_jade(B, d):            # Jade Phantom: jade panels glowing on the receiver
    for s in (1, -1):
        _box(B, s * 0.0212 if s > 0 else -0.0222, s * 0.0222 if s > 0 else -0.0212, 0.020, 0.090, -0.012, 0.020, "glow")
        _box(B, s * 0.0172 if s > 0 else -0.0182, s * 0.0182 if s > 0 else -0.0172, 0.240, 0.350, -0.018, 0.016, "glow")


SIGHTS = {"reddot": sight_reddot, "crystal": sight_crystal, "peep": sight_peep, "scope": sight_scope,
          "serpent": sight_serpent, "moon": sight_moon, "crown": sight_crown}
STOCKS = {"skeleton": stock_skeleton, "thumbhole": stock_thumbhole, "wood": stock_wood, "heavy": stock_heavy,
          "ornate": stock_ornate}
EXTRAS = {"Frostbite": extra_frost, "VerdantStalker": extra_leaves, "Stormbreaker": extra_lightning,
          "Emberfall": extra_embers, "Moonshadow": extra_crescents, "IronwoodSentinel": extra_rivets,
          "JadePhantom": extra_jade}


LIMBS.update({"forward": limbs_forward, "straight": limbs_straight, "compound": limbs_compound, "deflex": limbs_deflex})


def build(key):
    """(mesh, atlas) of one crossbow in the Hunting Rifle's frame."""
    d = BY_KEY[key]
    A = make_atlas(d)
    B = K.Builder(A)
    STOCKS[d["stock"]](B, d)
    grip(B, d)
    receiver(B, d)
    prod_mount(B, d)
    tips = LIMBS[d["limbs"]](B, d)
    string(B, tips[0])
    stirrup(B, d)
    SIGHTS[d["sight"]](B, d)
    if key in EXTRAS:
        EXTRAS[key](B, d)
    return B.m.check(item_id(key)), A


# =========================================================================== the bolt (ammunition)
BOLT_GLOW = (255, 220, 160)   # the same warm white as the flying bolt (client/JC_Client.lua)


def build_bolt():
    """One crossbow bolt along +Y (for the icon): shaft, glowing fletching and nock, steel tip.
    0.11.2 (Jamie's screenshot: a dropped bolt was two specks): the glow uses the blades'
    layout so the jc_glow shader lights it, and build_bolt_ground() lays it flat."""
    A = BL.GlowAtlas(background=(120, 120, 126, 255))
    A.add("shaft", matte((150, 152, 160), 16, 64, 11, speck=0.02))
    A.add("tip", matte((200, 204, 212), 16, 16, 13, speck=0.01))
    A.add("vane", glow_tex(BOLT_GLOW, 32, 32), glow=True)
    A.add("nock", glow_tex(_mix(BOLT_GLOW, (255, 255, 255), 0.3), 16, 16), glow=True)
    A.finish()
    B = K.Builder(A)
    tube(B, [(0, -0.18, 0), (0, 0.0, 0), (0, 0.16, 0)], [0.0045, 0.0045, 0.0045], "shaft", nu=8)
    tube(B, [(0, 0.16, 0), (0, 0.185, 0), (0, 0.205, 0)], [0.0065, 0.0045, 0.0005], "tip", nu=8)
    tube(B, [(0, -0.192, 0), (0, -0.186, 0), (0, -0.180, 0)], [0.0055, 0.0055, 0.0055], "nock", nu=8)
    for k in range(3):
        a = TAU * k / 3 + math.pi / 2
        dx, dz = math.cos(a), math.sin(a)
        p = [(0.004 * dx, -0.178, 0.004 * dz), (0.004 * dx, -0.100, 0.004 * dz), (0.020 * dx, -0.122, 0.020 * dz),
             (0.020 * dx, -0.172, 0.020 * dz)]
        B.m.quad(p, A.uv("vane"), two_sided=True)
    return B.m.check(BOLT_ID), A


def build_bolt_ground(m):
    """The bolt lying on the floor: world models stand on +Y, so the bolt is turned to lie
    along X, one fletch up, resting on the ground (y >= 0)."""
    import copy
    R = core._rot("z", -90)
    V = np.array([R @ np.asarray(v) for v in m.v])
    V[:, 1] -= V[:, 1].min()
    g = copy.copy(m)
    g.v = list(V)
    g.n = [R @ np.asarray(n) for n in m.n]
    return g


# =========================================================================== pictures
def _upright(m):
    """For pictures: Z-up crossbow turned Y-up (the renderers' up), pointing away (-Z)."""
    import copy
    R = core._rot("x", -90)
    mm = copy.copy(m)
    mm.v = [R @ np.asarray(v) for v in m.v]
    mm.n = [R @ np.asarray(n) for n in m.n]
    return mm


def _turned(m, deg):
    """Turned about Z (seen from above) and centred: the renderers frame round the origin."""
    import copy
    R = core._rot("z", deg)
    V = np.array([R @ np.asarray(v) for v in m.v])
    c = (V.min(0) + V.max(0)) / 2
    c[2] = 0.0
    mm = copy.copy(m)
    mm.v = list(V - c)
    mm.n = [R @ np.asarray(n) for n in m.n]
    return mm


def icon(m, A):
    """32x32 inventory icon: seen from above, on the diagonal, glowing."""
    im = BL.lit_and_glow(_turned(m, -45), A, yaw=0, pitch=0, size=128, fit=0.84, outline=(30, 24, 40))
    return im.resize((32, 32), Image.LANCZOS)


def sticker(m, A, size=128):
    return BL.lit_and_glow(_turned(m, -35), A, yaw=0, pitch=0, size=size, fit=0.92, outline=(255, 255, 255))


def turntable(m, A, frames=16, size=320):
    return BL.turntable(_upright(m), A, frames=frames, size=size, pitch=24)


def bolt_icon(m, A):
    im = BL.lit_and_glow(_turned(m, -45), A, yaw=0, pitch=0, size=128, fit=0.86, outline=(40, 36, 44))
    return im.resize((32, 32), Image.LANCZOS)
