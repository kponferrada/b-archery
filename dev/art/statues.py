"""Jamie's Treasures - Velvet Eclipse: Glamour & Fantasy Statues (0.8.0).

20 original adult fantasy heroines as premium display statues: tall anime-style
proportions (about 7.5 heads), a painted face, sculpted hair, a gown or armour,
accessories and a display base that grows more elaborate with rarity.

Built from smooth parametric shapes (ellipsoids, swept tubes, lathed profiles) like
the rest of the mod's art: original, no third-party assets. Not a hand-sculpted
mesh: faces are painted, fabric folds are shaped waves, so the look is a clean
stylised statue rather than a high-poly collector figure.

Scale: the statue (base + figure) is about 0.28 m in the model file, ~1.75x a Jamie's
Treasures mini figure (0.15-0.18 m), drawn at the same model scale (1.6) in game.
Front = +Z, up = +Y, origin = the centre of the base's underside (sits on the floor).

Rolled out one at a time (dev/catalog.py VELVET_ENABLED): the prototype is tested
in game before the other 19 are built.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import core
import kawaii as K
import meadow as MW

TAU = 2 * math.pi
SS = K.SS
FIG_H = 0.250          # top of the head above the base top (m)
STATUE_TARGET = 0.28   # base + figure, for the size report


# =========================================================================== the 20 designs
# Colours are RGB. hair2 = the shade; eyes; skin; gown/gown2 = main and secondary
# fabric; trim = metal trim; gem = the glowing accent; base / base2 = plinth colours.
# rarity decides the base (simple disc -> tiered -> ornate -> centrepiece).
DESIGNS = [
    dict(key="LunariaNoctis", name="Lunaria Noctis", title="Moon Witch", rarity="Epic",
         lore="Lunaria Noctis, the Moon Witch. Silver hair, violet eyes, a midnight gown and a crescent staff that keeps the night's light.",
         skin=(248, 226, 214), hair=(218, 222, 236), hair2=(150, 156, 184), eyes=(150, 92, 214),
         gown=(30, 30, 74), gown2=(70, 56, 140), trim=(214, 218, 232), gem=(196, 160, 255),
         base=(36, 32, 66), base2=(214, 218, 232), lips=(206, 120, 150),
         hair_style="long", outfit="gown_cape", pose="staff_orb", props=["witch_hat", "crescent_staff", "moon_orb"],
         base_motif="moon"),
    dict(key="Rosavelle", name="Rosavelle", title="Crimson Spellcaster", rarity="Common",
         lore="Rosavelle, the Crimson Spellcaster. Crimson hair, a burgundy gown and roses that bloom from her spells.",
         hair=(176, 30, 52), eyes=(196, 60, 80), gown=(110, 20, 44), gown2=(170, 40, 70), trim=(222, 176, 96), gem=(255, 90, 120),
         props=["rose_magic"]),
    dict(key="IsoldeFrostveil", name="Isolde Frostveil", title="Ice Oracle", rarity="Uncommon",
         lore="Isolde Frostveil, the Ice Oracle. Pale-blue hair under a crystal crown, in a gown of flowing frost.",
         hair=(176, 214, 240), eyes=(90, 170, 230), gown=(196, 226, 248), gown2=(130, 180, 226), trim=(236, 248, 255), gem=(150, 220, 255),
         props=["crystal_crown"]),
    dict(key="SeraphineVoss", name="Seraphine Voss", title="Emerald Enchantress", rarity="Common",
         lore="Seraphine Voss, the Emerald Enchantress. Black hair, an emerald gown and ornate gold.",
         hair=(28, 26, 34), eyes=(40, 170, 110), gown=(20, 110, 70), gown2=(40, 150, 100), trim=(226, 180, 70), gem=(90, 230, 150),
         props=["gold_circlet"]),
    dict(key="AureliaVane", name="Aurelia Vane", title="Golden Valkyrie", rarity="Epic",
         lore="Aurelia Vane, the Golden Valkyrie. Blonde hair, white-and-gold armour and elegant wings.",
         hair=(246, 214, 120), eyes=(70, 140, 220), gown=(240, 240, 246), gown2=(226, 186, 80), trim=(236, 190, 70), gem=(255, 226, 130),
         props=["wings_feather", "winged_helm"]),
    dict(key="VeyraBlackthorn", name="Veyra Blackthorn", title="Obsidian Queen", rarity="Uncommon",
         lore="Veyra Blackthorn, the Obsidian Queen. Dark-blue hair and black-and-silver armour.",
         hair=(30, 42, 96), eyes=(120, 140, 220), gown=(26, 24, 32), gown2=(150, 156, 172), trim=(196, 200, 214), gem=(130, 150, 255),
         props=["thorn_crown"]),
    dict(key="KaelithEmbercrest", name="Kaelith Embercrest", title="Flame Commander", rarity="Uncommon",
         lore="Kaelith Embercrest, the Flame Commander. Red hair, red-and-gold armour and a spear.",
         hair=(210, 56, 34), eyes=(240, 150, 40), gown=(150, 30, 26), gown2=(226, 170, 60), trim=(236, 186, 70), gem=(255, 140, 50),
         props=["spear"]),
    dict(key="ThalassaWynn", name="Thalassa Wynn", title="Tidal Champion", rarity="Common",
         lore="Thalassa Wynn, the Tidal Champion. Teal hair and bronze armour shaped like waves.",
         hair=(40, 160, 160), eyes=(40, 190, 190), gown=(30, 90, 110), gown2=(180, 120, 60), trim=(200, 140, 70), gem=(90, 230, 220),
         props=["trident"]),
    dict(key="CarmillaVesper", name="Carmilla Vesper", title="Scarlet Countess", rarity="Rare",
         lore="Carmilla Vesper, the Scarlet Countess. A gothic black-and-crimson dress and a bat-wing cape.",
         hair=(40, 30, 40), eyes=(220, 40, 60), gown=(24, 18, 24), gown2=(160, 20, 40), trim=(200, 170, 110), gem=(255, 40, 70),
         props=["batwing_cape"]),
    dict(key="Veloura", name="Veloura", title="Velvet Temptress", rarity="Rare",
         lore="Veloura, the Velvet Temptress. Violet hair, horns and wings, in plum velvet.",
         hair=(150, 80, 200), eyes=(230, 120, 220), gown=(90, 30, 90), gown2=(140, 60, 150), trim=(220, 180, 230), gem=(240, 140, 255),
         props=["horns_small", "wings_bat"]),
    dict(key="Noctelle", name="Noctelle", title="Black Rose", rarity="Uncommon",
         lore="Noctelle, the Black Rose. Silver hair, a black gown and a lace parasol.",
         hair=(214, 216, 226), eyes=(160, 60, 90), gown=(22, 20, 26), gown2=(70, 60, 76), trim=(200, 196, 210), gem=(180, 40, 70),
         props=["parasol", "black_rose"]),
    dict(key="Malvera", name="Malvera", title="Abyssal Duchess", rarity="Rare",
         lore="Malvera, the Abyssal Duchess. Dark-red hair, curved horns, black and gold.",
         hair=(120, 20, 30), eyes=(240, 170, 40), gown=(20, 16, 20), gown2=(200, 150, 60), trim=(226, 176, 70), gem=(255, 100, 40),
         props=["horns_curved"]),
    dict(key="MarinaSolenne", name="Marina Solenne", title="Pearl Goddess", rarity="Common",
         lore="Marina Solenne, the Pearl Goddess. Turquoise hair and a gown like the shallow sea.",
         hair=(60, 200, 196), eyes=(40, 160, 200), gown=(150, 220, 226), gown2=(240, 246, 250), trim=(250, 240, 230), gem=(255, 250, 240),
         props=["pearls"]),
    dict(key="CoralineBloom", name="Coraline Bloom", title="Summer Muse", rarity="Common",
         lore="Coraline Bloom, the Summer Muse. Coral-pink hair and a stylish summer dress.",
         hair=(246, 130, 120), eyes=(80, 170, 200), gown=(250, 236, 200), gown2=(246, 140, 120), trim=(250, 210, 120), gem=(255, 180, 150),
         props=["sun_hat"]),
    dict(key="NerissaTidewhisper", name="Nerissa Tidewhisper", title="Mermaid Queen", rarity="Rare",
         lore="Nerissa Tidewhisper, the Mermaid Queen. Lavender hair, a shell crown and seafoam silks.",
         hair=(186, 160, 230), eyes=(80, 200, 200), gown=(150, 226, 210), gown2=(200, 180, 240), trim=(250, 226, 220), gem=(160, 240, 230),
         props=["shell_crown"]),
    dict(key="SolaraVienne", name="Solara Vienne", title="Sunlit Goddess", rarity="Common",
         lore="Solara Vienne, the Sunlit Goddess. Golden-brown hair in white and gold.",
         hair=(176, 120, 60), eyes=(210, 150, 50), gown=(248, 246, 240), gown2=(236, 196, 90), trim=(240, 196, 80), gem=(255, 220, 120),
         props=["sun_diadem"]),
    dict(key="Elarielle", name="Elarielle", title="Star Empress", rarity="Legendary",
         lore="Elarielle, the Star Empress. White hair, an ivory gown and a halo of stars.",
         hair=(250, 250, 252), eyes=(130, 170, 250), gown=(246, 240, 226), gown2=(220, 200, 150), trim=(236, 200, 110), gem=(255, 240, 180),
         props=["star_halo"]),
    dict(key="Amorette", name="Amorette", title="Heartkeeper", rarity="Uncommon",
         lore="Amorette, the Heartkeeper. Pink hair, feathered wings and heart jewellery.",
         hair=(246, 150, 190), eyes=(220, 80, 140), gown=(250, 200, 220), gown2=(240, 120, 160), trim=(240, 200, 120), gem=(255, 110, 160),
         props=["wings_feather", "hearts"]),
    dict(key="AstrielleVoss", name="Astrielle Voss", title="Cosmic Regent", rarity="Epic",
         lore="Astrielle Voss, the Cosmic Regent. Midnight-blue hair and a cape full of galaxies.",
         hair=(30, 36, 110), eyes=(200, 140, 255), gown=(20, 20, 50), gown2=(120, 80, 200), trim=(210, 200, 250), gem=(200, 160, 255),
         props=["galaxy_cape", "regent_crown"]),
    dict(key="Luminelle", name="Luminelle", title="Eternal Dream", rarity="Legendary",
         lore="Luminelle, the Eternal Dream. Lilac hair, crystal wings and a gown that drifts like sleep.",
         hair=(200, 170, 240), eyes=(150, 120, 240), gown=(230, 214, 250), gown2=(180, 150, 236), trim=(240, 230, 255), gem=(220, 200, 255),
         props=["wings_crystal"]),
]
BY_KEY = {d["key"]: d for d in DESIGNS}
assert len(DESIGNS) == 20 and len(BY_KEY) == 20


# --------------------------------------------------------------------------- per-character styling
# pose (POSES), hair_style (long | wavy | flowing | side_swept | ponytail | bun | bob | braid),
# outfit (gown | gown_cape | armor), skirt (gown | train | tiered | layered | short | mermaid),
# sleeve (bell | bare | bracer | long | puff), pattern (fabric texture), props, motif (base).
STYLE = {
    "LunariaNoctis": dict(pose="staff_orb", hair_style="long", outfit="gown_cape", pattern="stars",
                          props=["witch_hat", "crescent_staff", "moon_orb"], motif="moon"),
    "Rosavelle": dict(pose="spell_raise", hair_style="wavy", pattern="damask", sleeve="bell", props=["rose_magic"], motif="roses",
                      base=(70, 20, 34)),
    "IsoldeFrostveil": dict(pose="hold_front", hair_style="long", pattern="frost", sleeve="long", props=["crystal_crown", "ice_orb"],
                            motif="snow", skin=(250, 234, 228), base=(60, 90, 130)),
    "SeraphineVoss": dict(pose="hip_raise", hair_style="bun", pattern="satin", sleeve="bare", props=["gold_circlet", "emerald"],
                          motif="leaves", skin=(236, 206, 186), base=(20, 60, 44), base2=(226, 180, 70)),
    "AureliaVane": dict(pose="weapon_plant", hair_style="braid", outfit="armor", pattern="satin", plate=(236, 236, 242),
                        props=["wings_feather", "winged_helm", "sword"], motif="sun", base=(240, 236, 226), base2=(226, 180, 70)),
    "VeyraBlackthorn": dict(pose="scepter", hair_style="bob", outfit="armor", pattern="damask", plate=(56, 58, 70),
                            props=["thorn_crown", "scepter"], motif="thorns", skin=(244, 224, 220), base=(24, 24, 34)),
    "KaelithEmbercrest": dict(pose="weapon_diag", hair_style="ponytail", outfit="armor", pattern="satin", plate=(200, 50, 40),
                              props=["spear"], motif="flames", skin=(238, 198, 168), base=(60, 20, 18)),
    "ThalassaWynn": dict(pose="weapon_plant", hair_style="ponytail", outfit="armor", pattern="waves", plate=(196, 132, 70),
                         props=["trident"], motif="waves", skin=(206, 150, 112), base=(24, 70, 84)),
    "CarmillaVesper": dict(pose="hand_chest", hair_style="long", skirt="tiered", pattern="lace", sleeve="puff", collar=True,
                           props=["batwing_cape"], motif="bats", skin=(246, 230, 228), base=(30, 16, 22)),
    "Veloura": dict(pose="hair_touch", hair_style="wavy", pattern="velvet", sleeve="bare", props=["horns_small", "wings_bat"],
                    motif="ribbons", skin=(242, 214, 214), base=(60, 26, 66)),
    "Noctelle": dict(pose="parasol", hair_style="side_swept", skirt="tiered", pattern="lace", sleeve="long", collar=True,
                     props=["parasol", "black_rose"], motif="roses", base=(26, 24, 30)),
    "Malvera": dict(pose="duchess", hair_style="side_swept", pattern="damask", sleeve="bell", skirt="train", train=0.07,
                    props=["horns_curved", "dark_orb"], motif="flames", skin=(240, 220, 214), base=(24, 18, 20), base2=(226, 176, 70)),
    "MarinaSolenne": dict(pose="offer", hair_style="wavy", pattern="waves", sleeve="bare", props=["pearls"], motif="waves",
                          skin=(226, 184, 154), base=(40, 120, 140)),
    "CoralineBloom": dict(pose="hat_hold", hair_style="bob", skirt="short", pattern="flowers", sleeve="bare", props=["sun_hat"],
                          motif="flowers", skin=(242, 206, 178), base=(250, 196, 170)),
    "NerissaTidewhisper": dict(pose="open_arms", hair_style="flowing", skirt="mermaid", pattern="waves", sleeve="bare",
                               props=["shell_crown"], motif="shells", skin=(236, 214, 206), base=(40, 110, 130)),
    "SolaraVienne": dict(pose="arms_up", hair_style="long", pattern="satin", sleeve="bare", props=["sun_diadem", "sun_disc"],
                         motif="suns", skin=(176, 120, 88), base=(240, 226, 196)),
    "Elarielle": dict(pose="open_arms", hair_style="flowing", skirt="train", train=0.09, pattern="stars", sleeve="long",
                      props=["star_halo"], motif="stars", outfit="gown_cape", base=(232, 224, 206), base2=(226, 186, 90)),
    "Amorette": dict(pose="heart_hold", hair_style="wavy", pattern="hearts", sleeve="puff", props=["small_wings", "hearts"],
                     motif="hearts", base=(250, 206, 222)),
    "AstrielleVoss": dict(pose="scepter", hair_style="long", pattern="galaxy", sleeve="long", skirt="train", train=0.06,
                          props=["galaxy_cape", "regent_crown", "star_scepter"], motif="cosmos", skin=(232, 206, 196), base=(18, 16, 42)),
    "Luminelle": dict(pose="dream", hair_style="flowing", skirt="layered", pattern="stars", sleeve="bare",
                      props=["wings_crystal"], motif="dream", base=(220, 210, 246)),
}


def item_id(key):
    return "JT_Velvet_" + key


# =========================================================================== texture
def _clamp(c):
    return tuple(int(max(0, min(255, v))) for v in c)


def _shade(c, k):
    return _clamp(v * k for v in c)


def _mix(a, b, t):
    return _clamp(a[i] + (b[i] - a[i]) * t for i in range(3))


def _vgrad(size, top, bottom):
    im = Image.new("RGBA", (size, size))
    d = ImageDraw.Draw(im)
    for y in range(size):
        d.line([(0, y), (size, y)], fill=_mix(top, bottom, y / (size - 1)) + (255,))
    return im


def paint_face(d, w=512, h=256):
    """An adult anime face on the head's front (longitude across, latitude down)."""
    p = K.Painter(w, h, d["skin"])
    eye = d["eyes"]
    lash = (44, 30, 40, 255)
    for side in (-1, 1):
        x = side * 0.33
        y = -0.15
        # eye white, iris (dark rim, colour, light lower half), pupil, highlights
        p.ellipse(x, y, 0.20, 0.13, (252, 250, 252, 255))
        p.ellipse(x + side * 0.012, y - 0.010, 0.115, 0.125, _shade(eye, 0.55) + (255,))
        p.ellipse(x + side * 0.012, y - 0.020, 0.098, 0.100, eye + (255,))
        p.ellipse(x + side * 0.012, y - 0.055, 0.075, 0.050, _mix(eye, (255, 255, 255), 0.40) + (255,))
        p.ellipse(x + side * 0.012, y + 0.000, 0.042, 0.055, _shade(eye, 0.30) + (255,))
        p.ellipse(x - side * 0.030, y + 0.045, 0.032, 0.032, (255, 255, 255, 255))
        p.ellipse(x + side * 0.045, y - 0.060, 0.016, 0.016, (255, 255, 255, 230))
        # upper lash line: thick, with a flick at the outer corner; thin lower line
        p.line([(x - side * 0.22, y + 0.04), (x - side * 0.08, y + 0.125), (x + side * 0.10, y + 0.125), (x + side * 0.22, y + 0.07),
                (x + side * 0.28, y + 0.13)], lash, 0.040)
        p.line([(x - side * 0.14, y - 0.115), (x + side * 0.16, y - 0.105)], (120, 80, 90, 200), 0.010)
        # brow: thin and arched
        p.line([(x - side * 0.18, y + 0.25), (x, y + 0.29), (x + side * 0.20, y + 0.26)], _shade(d["hair2"], 0.7) + (255,), 0.018)
        # blush
        p.ellipse(x + side * 0.06, -0.34, 0.11, 0.035, _mix(d["skin"], (250, 150, 160), 0.40) + (255,))
    # nose: a small shadow; mouth: a soft closed smile
    p.line([(0.012, -0.33), (0.0, -0.37)], _shade(d["skin"], 0.82) + (255,), 0.014)
    p.line([(-0.075, -0.475), (0.0, -0.488), (0.075, -0.475)], d["lips"] + (255,), 0.024)
    p.line([(-0.05, -0.483), (0.05, -0.483)], _shade(d["lips"], 0.7) + (255,), 0.009)
    return p.done(w, h)


def hair_tex(d, size=128):
    """Long strands: soft vertical streaks of the hair colour and its shade."""
    im = _vgrad(size * SS, _mix(d["hair"], (255, 255, 255), 0.15), d["hair"])
    dr = ImageDraw.Draw(im)
    rng = np.random.default_rng(7)
    S = size * SS
    for _ in range(70):
        x = rng.uniform(0, S)
        col = _mix(d["hair"], d["hair2"], rng.uniform(0.2, 0.8)) + (255,)
        dr.line([(x, 0), (x + rng.uniform(-6, 6) * SS, S)], fill=col, width=int(rng.uniform(1, 3) * SS))
    for _ in range(12):
        x = rng.uniform(0, S)
        dr.line([(x, 0), (x, S)], fill=(255, 255, 255, 120), width=SS)
    return im.resize((size, size), Image.LANCZOS)


def starry(base, accent, size=256, n=220, seed=3):
    """Fabric with a scatter of tiny stars (midnight gowns, capes)."""
    im = _vgrad(size * SS, _mix(base, accent, 0.25), base)
    dr = ImageDraw.Draw(im)
    rng = np.random.default_rng(seed)
    S = size * SS
    for _ in range(n):
        x, y = rng.uniform(0, S), rng.uniform(0, S)
        r = rng.uniform(0.35, 1.1) * SS
        dr.ellipse([x - r, y - r, x + r, y + r], fill=_mix(accent, (255, 255, 255), rng.uniform(0.3, 0.8)) + (255,))
    return im.resize((size, size), Image.LANCZOS)


def satin(c, size=64):
    """Fabric with a soft sheen across it."""
    im = Image.new("RGBA", (size, size))
    a = np.zeros((size, size, 4), dtype=np.uint8)
    for x in range(size):
        k = 0.86 + 0.20 * math.sin(x / size * TAU * 2) ** 2
        a[:, x, :3] = _shade(c, k)
        a[:, x, 3] = 255
    im = Image.fromarray(a, "RGBA")
    return im


def metal(c, size=64):
    return _vgrad(size, _mix(c, (255, 255, 255), 0.45), _shade(c, 0.70))


def pattern_tex(d, size=256):
    """The gown fabric, by design: stars, satin, damask, frost, lace, velvet, waves,
    flowers, hearts or galaxy."""
    p = d.get("pattern", "satin")
    base, acc = d["gown"], d["gem"]
    if p == "stars":
        return starry(base, acc)
    if p == "galaxy":
        im = _vgrad(size * SS, _mix(base, d["gown2"], 0.3), base)
        a = np.asarray(im).astype(np.float32)
        rng = np.random.default_rng(21)
        S = size * SS
        yy, xx = np.mgrid[0:S, 0:S]
        for _ in range(7):
            cx, cy, r = rng.uniform(0, S), rng.uniform(0, S), rng.uniform(0.12, 0.3) * S
            col = np.array(_mix(d["gown2"], acc, rng.uniform(0, 1)), dtype=np.float32)
            w = np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r))[..., None] * 0.55
            a[..., :3] = a[..., :3] * (1 - w) + col * w
        im = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA").resize((size, size), Image.LANCZOS)
        st = starry((0, 0, 0), (255, 255, 255), size=size, n=260, seed=9)
        return Image.composite(st, im, st.convert("L").point(lambda v: 255 if v > 60 else 0))
    im = satin(base, size)
    d_ = ImageDraw.Draw(im)
    k = size / 64
    light = _mix(base, (255, 255, 255), 0.22) + (255,)
    dark = _shade(base, 0.75) + (255,)
    if p == "damask":
        for y in range(0, size, int(16 * k)):
            for x in range(0, size, int(16 * k)):
                o = int(8 * k) if (y // int(16 * k)) % 2 else 0
                cx, cy = x + o, y
                d_.polygon([(cx, cy - 5 * k), (cx + 4 * k, cy), (cx, cy + 5 * k), (cx - 4 * k, cy)], outline=light, width=max(1, int(k)))
    elif p == "frost":
        rng = np.random.default_rng(4)
        for _ in range(14):
            x, y = rng.uniform(0, size), rng.uniform(0, size)
            for j in range(6):
                a = TAU * j / 6
                d_.line([(x, y), (x + 8 * k * math.cos(a), y + 8 * k * math.sin(a))], fill=(255, 255, 255, 255), width=max(1, int(k * 0.6)))
    elif p == "lace":
        for y in range(0, size, int(8 * k)):
            for x in range(0, size, int(8 * k)):
                d_.ellipse([x, y, x + 3 * k, y + 3 * k], outline=_mix(base, d["gown2"], 0.7) + (255,), width=max(1, int(k * 0.5)))
    elif p == "velvet":
        im = _vgrad(size, _mix(base, (255, 255, 255), 0.12), _shade(base, 0.8))
    elif p == "waves":
        for y in range(0, size, int(10 * k)):
            pts = [(x, y + 2.5 * k * math.sin(x / (6 * k))) for x in range(0, size + 1, max(1, int(k)))]
            d_.line(pts, fill=light, width=max(1, int(k * 0.7)))
    elif p == "flowers":
        rng = np.random.default_rng(6)
        for _ in range(18):
            x, y = rng.uniform(0, size), rng.uniform(0, size)
            col = _mix(d["gown2"], (255, 255, 255), rng.uniform(0, 0.3)) + (255,)
            for j in range(5):
                a = TAU * j / 5
                d_.ellipse([x + 3 * k * math.cos(a) - 2 * k, y + 3 * k * math.sin(a) - 2 * k, x + 3 * k * math.cos(a) + 2 * k,
                            y + 3 * k * math.sin(a) + 2 * k], fill=col)
            d_.ellipse([x - 1.2 * k, y - 1.2 * k, x + 1.2 * k, y + 1.2 * k], fill=(250, 210, 110, 255))
    elif p == "hearts":
        rng = np.random.default_rng(8)
        for _ in range(16):
            x, y = rng.uniform(0, size), rng.uniform(0, size)
            r = rng.uniform(1.5, 3) * k
            d_.ellipse([x - r, y - r, x, y], fill=light)
            d_.ellipse([x, y - r, x + r, y], fill=light)
            d_.polygon([(x - r, y - r * 0.4), (x + r, y - r * 0.4), (x, y + r)], fill=light)
    return im


def feather_tex(c, size=64):
    im = _vgrad(size, _mix(c, (255, 255, 255), 0.3), _shade(c, 0.85))
    d_ = ImageDraw.Draw(im)
    d_.line([(size / 2, 0), (size / 2, size)], fill=_shade(c, 0.7) + (255,), width=2)
    for y in range(0, size, 6):
        d_.line([(size / 2, y), (0, y + 8)], fill=_shade(c, 0.9) + (255,), width=1)
        d_.line([(size / 2, y), (size, y + 8)], fill=_shade(c, 0.9) + (255,), width=1)
    return im


def scales_tex(c, c2, size=128):
    im = _vgrad(size, _mix(c, (255, 255, 255), 0.15), _shade(c, 0.8))
    d_ = ImageDraw.Draw(im)
    for row, y in enumerate(range(0, size, 8)):
        for x in range(-8 if row % 2 else -4, size, 8):
            d_.arc([x, y - 4, x + 8, y + 6], 0, 180, fill=_mix(c, c2, 0.6) + (255,), width=1)
    return im


def crystal_tex(c, size=64):
    im = _vgrad(size, _mix(c, (255, 255, 255), 0.65), _mix(c, (255, 255, 255), 0.1))
    d_ = ImageDraw.Draw(im)
    for k in range(4):
        d_.line([(k * 18, 0), (k * 18 + 20, size)], fill=(255, 255, 255, 255), width=2)
    return im


MOTIF_SYMBOL = {"moon": "moon", "roses": "rose", "snow": "snow", "leaves": "leaf", "sun": "sun", "thorns": "diamond",
                "flames": "flame", "waves": "wave", "bats": "heart", "ribbons": "heart", "shells": "shell", "flowers": "flower",
                "suns": "sun", "stars": "star", "hearts": "heart", "cosmos": "star", "dream": "diamond"}


def _symbol(dr, kind, x, y, r, col, bg):
    if kind == "moon":
        dr.ellipse([x - r, y - r, x + r, y + r], fill=col)
        dr.ellipse([x - r * 0.4, y - r * 1.1, x + r * 1.4, y + r * 0.7], fill=bg)
    elif kind in ("star", "sun"):
        n = 8 if kind == "sun" else 5
        pts = []
        for i in range(n * 2):
            rr = r if i % 2 == 0 else r * (0.6 if kind == "sun" else 0.42)
            a = -math.pi / 2 + i * math.pi / n
            pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
        dr.polygon(pts, fill=col)
    elif kind == "heart":
        dr.ellipse([x - r, y - r * 0.8, x, y + r * 0.1], fill=col)
        dr.ellipse([x, y - r * 0.8, x + r, y + r * 0.1], fill=col)
        dr.polygon([(x - r * 0.95, y - r * 0.2), (x + r * 0.95, y - r * 0.2), (x, y + r)], fill=col)
    elif kind == "snow":
        for j in range(3):
            a = math.pi * j / 3
            dr.line([(x - r * math.cos(a), y - r * math.sin(a)), (x + r * math.cos(a), y + r * math.sin(a))], fill=col, width=max(2, int(r / 4)))
    elif kind == "flame":
        dr.polygon([(x, y - r), (x + r * 0.6, y + r * 0.2), (x, y + r), (x - r * 0.6, y + r * 0.2)], fill=col)
    elif kind == "wave":
        pts = [(x - r + 2 * r * t / 10, y + r * 0.35 * math.sin(t / 10 * TAU)) for t in range(11)]
        dr.line(pts, fill=col, width=max(2, int(r / 3)))
    elif kind in ("rose", "flower"):
        for j in range(5):
            a = TAU * j / 5
            dr.ellipse([x + r * 0.5 * math.cos(a) - r * 0.45, y + r * 0.5 * math.sin(a) - r * 0.45,
                        x + r * 0.5 * math.cos(a) + r * 0.45, y + r * 0.5 * math.sin(a) + r * 0.45], fill=col)
        dr.ellipse([x - r * 0.3, y - r * 0.3, x + r * 0.3, y + r * 0.3], fill=bg)
    elif kind == "leaf":
        dr.ellipse([x - r * 0.45, y - r, x + r * 0.45, y + r], fill=col)
    elif kind == "shell":
        dr.pieslice([x - r, y - r, x + r, y + r], 180, 360, fill=col)
    else:   # diamond
        dr.polygon([(x, y - r), (x + r * 0.6, y), (x, y + r), (x - r * 0.6, y)], fill=col)


def base_top_art(d, size=256):
    """The plinth's top: a double ring and the character's motif round the rim."""
    S = size * SS
    bg = _shade(d["base"], 1.15) + (255,)
    im = Image.new("RGBA", (S, S), bg)
    dr = ImageDraw.Draw(im)
    ring = d["base2"] + (255,)
    dr.ellipse([S * 0.03, S * 0.03, S * 0.97, S * 0.97], outline=ring, width=int(S * 0.025))
    dr.ellipse([S * 0.10, S * 0.10, S * 0.90, S * 0.90], outline=_shade(d["base2"], 0.8) + (255,), width=int(S * 0.008))
    kind = MOTIF_SYMBOL.get(d.get("motif"), "star")
    n = 8
    for k in range(n):
        a = TAU * k / n - math.pi / 2
        x, y = S / 2 + S * 0.42 * math.cos(a), S / 2 + S * 0.42 * math.sin(a)
        if kind == "moon" and d.get("motif") == "moon":   # Lunaria keeps her moon phases
            r = S * 0.03
            dr.ellipse([x - r, y - r, x + r, y + r], fill=ring)
            off = r * (-1 + 2 * k / 8) * 1.6
            dr.ellipse([x - r + off, y - r, x + r + off, y + r], fill=bg)
        else:
            _symbol(dr, kind, x, y, S * 0.032, ring, bg)
    return im.resize((size, size), Image.LANCZOS)


def nameplate(d, W=256, H=48):
    S = SS
    im = Image.new("RGBA", (W * S, H * S), _shade(d["base"], 0.9) + (255,))
    dr = ImageDraw.Draw(im)
    f = K.font(24 * S)
    t = d["name"].upper()
    tw = dr.textlength(t, font=f)
    dr.text(((W * S - tw) / 2, 10 * S), t, font=f, fill=d["base2"] + (255,))
    return im.resize((W, H), Image.LANCZOS)


def atlas(d):
    A = core.Atlas(1024, background=d["skin"] + (255,))
    A.add("face", paint_face(d))
    A.add("skin", K.swatch(d["skin"]))
    A.add("hair", hair_tex(d))
    A.add("hair2", K.swatch(d["hair2"]))
    A.add("gown", pattern_tex(d))
    A.add("gown2", satin(d["gown2"]))
    A.add("cape", starry(_shade(d["gown"], 0.85), d["gown2"], seed=5))
    A.add("trim", metal(d["trim"]))
    A.add("gold", metal((236, 190, 80)))
    A.add("gem", K.swatch(d["gem"], grad=False))
    A.add("gemcore", K.swatch(_mix(d["gem"], (255, 255, 255), 0.6), grad=False))
    A.add("staff", metal(_shade(d["trim"], 0.85)))
    A.add("dark", K.swatch((40, 34, 52)))
    A.add("base_top", base_top_art(d))
    A.add("base_side", K.swatch(d["base"]))
    A.add("base_trim", metal(d["base2"]))
    A.add("plate_name", nameplate(d))
    A.add("plate", metal(d.get("plate", d["gown2"])))
    A.add("blade", metal((226, 232, 242)))
    A.add("feather", feather_tex((252, 250, 246) if d["key"] != "Amorette" else (255, 236, 244)))
    A.add("feather2", feather_tex(_mix(d["gown2"], (255, 255, 255), 0.4)))
    A.add("lace", pattern_tex(dict(d, pattern="lace", gown=_mix(d["gown2"], (255, 255, 255), 0.35), gown2=d["gown"]), size=128))
    A.add("leaf", K.swatch((60, 110, 60)))
    A.add("pearl", metal((250, 244, 236)))
    A.add("straw", K.swatch((236, 214, 160)))
    A.add("galaxy", pattern_tex(dict(d, pattern="galaxy")))
    A.add("crystal", crystal_tex(d["gem"]))
    A.add("tail", scales_tex(d["gown"], d["gown2"]))
    A.add("cloud", _vgrad(64, (255, 255, 255), _mix(d["gown2"], (255, 255, 255), 0.6)))
    return A.finish()


# =========================================================================== geometry helpers
def _catmull(P, t):
    """Point on a Catmull-Rom curve through P at t in [0, 1]."""
    n = len(P) - 1
    s = min(max(t, 0.0), 1.0) * n
    i = min(int(s), n - 1)
    f = s - i
    p0 = P[max(i - 1, 0)]
    p1, p2 = P[i], P[i + 1]
    p3 = P[min(i + 2, n)]
    f2, f3 = f * f, f * f * f
    return 0.5 * ((2 * p1) + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f2 + (-p0 + 3 * p1 - 3 * p2 + p3) * f3)


def _interp(vals, t):
    n = len(vals) - 1
    s = min(max(t, 0.0), 1.0) * n
    i = min(int(s), n - 1)
    f = s - i
    return vals[i] + (vals[i + 1] - vals[i]) * f


def tube(B, pts, radii, region, nu=10, nv=None, depth=1.0, side=(1.0, 0.0, 0.0), caps=True):
    """A closed tube swept along a smooth curve through `pts`, radius `radii` (one per
    point, linear between). depth < 1 flattens it across `side`'s perpendicular (hair
    locks, capes). Ends close to a point."""
    P = [np.asarray(p, dtype=float) for p in pts]
    nv = nv or max(6, 4 * (len(P) - 1))
    side = np.asarray(side, dtype=float)
    rows = []
    for i in range(nv + 1):
        t = i / nv
        c = _catmull(P, t)
        tg = _catmull(P, min(t + 0.01, 1.0)) - _catmull(P, max(t - 0.01, 0.0))
        tg = tg / (np.linalg.norm(tg) or 1)
        a = side - tg * (side @ tg)
        if np.linalg.norm(a) < 1e-6:
            a = np.cross(tg, [0.0, 0.0, 1.0])
        a = a / np.linalg.norm(a)
        b = np.cross(tg, a)
        r = _interp(radii, t)
        rows.append((c, a, b * depth, r, tg))
    grid, uvs = [], []
    if caps:
        c, a, b, r, tg = rows[0]
        grid.append([c - tg * r * 0.3] * (nu + 1))
    for c, a, b, r, tg in rows:
        grid.append([c + r * (math.cos(TAU * j / nu) * a + math.sin(TAU * j / nu) * b) for j in range(nu + 1)])
    if caps:
        c, a, b, r, tg = rows[-1]
        grid.append([c + tg * r * 0.3] * (nu + 1))
    nr = len(grid)
    for i in range(nr):
        uvs.append([B.A.point(region, min(max(j / nu, 0.002), 0.998), min(max(i / (nr - 1), 0.002), 0.998)) for j in range(nu + 1)])
    _emit_grid(B, grid, uvs)


def _emit_grid(B, grid, uvs):
    """Normals from the grid, pointing away from each ring's centre."""
    nr, nc = len(grid), len(grid[0])
    N = []
    for i in range(nr):
        centre = np.mean(grid[i][:-1], axis=0)
        row = []
        for j in range(nc):
            a = grid[i][(j + 1) % (nc - 1)] - grid[i][(j - 1) % (nc - 1)]
            b = grid[min(i + 1, nr - 1)][j] - grid[max(i - 1, 0)][j]
            n = np.cross(a, b)
            if np.linalg.norm(n) < 1e-12:
                n = grid[i][j] - (np.mean(grid[1 if i == 0 else nr - 2][:-1], axis=0))
            if np.linalg.norm(grid[i][j] - centre) > 1e-9 and n @ (grid[i][j] - centre) < 0:
                n = -n
            elif np.linalg.norm(grid[i][j] - centre) <= 1e-9:
                other = np.mean(grid[1 if i == 0 else nr - 2][:-1], axis=0)
                n = grid[i][j] - other
            row.append(n / (np.linalg.norm(n) or 1))
        N.append(row)
    B._emit(grid, N, uvs)


def crescent(B, centre, R, r, region, normal=(0, 0, 1), up=(0, 1, 0), open_deg=70, nu=7, nv=18):
    """A crescent moon: a tube along a circle arc, fat in the middle, pointed at the tips.
    The gap (open_deg wide) faces +`up` rotated..., i.e. the horns point up-right."""
    n = np.asarray(normal, dtype=float)
    n = n / np.linalg.norm(n)
    u = np.asarray(up, dtype=float)
    u = u - n * (u @ n)
    u = u / np.linalg.norm(u)
    v = np.cross(n, u)
    a0 = math.radians(open_deg / 2)
    a1 = TAU - a0
    pts, radii = [], []
    k = 12
    for i in range(k + 1):
        a = a0 + (a1 - a0) * i / k
        pts.append(np.asarray(centre) + R * (math.cos(a) * u + math.sin(a) * v))
        radii.append(r * (0.12 + 0.88 * math.sin(math.pi * i / k)))
    tube(B, pts, radii, region, nu=nu, nv=nv, depth=0.55, side=n)


def star4(B, centre, r, region, depth=0.35, facing=(0, 0, 1)):
    """A four-point sparkle star (two flattened crossing spindles)."""
    c = np.asarray(centre, dtype=float)
    f = np.asarray(facing, dtype=float)
    for d_ in ((0, 1, 0), (1, 0, 0)):
        d_ = np.asarray(d_, dtype=float)
        tube(B, [c - d_ * r, c, c + d_ * r], [0.0005, r * 0.32, 0.0005], region, nu=4, nv=6, depth=depth, side=f, caps=False)


# =========================================================================== the body
# Units: 1.0 = the top of the head (the figure is scaled by FIG_H). Front = +Z.
# +X is her left side as you face her; "R" in a pose is the +X arm.
SHOULDER = 0.084


def head_y():
    return 0.930


POSES = {
    # each arm: shoulder -> elbow -> wrist; hand: grip | open_up | open | relaxed | hip | cup
    # sway: the skirt's drift at the floor
    "staff_orb": dict(R=[(0.128, 0.672, 0.020), (0.150, 0.585, 0.060)], R_hand="grip",
                      L=[(-0.140, 0.700, 0.040), (-0.152, 0.790, 0.110)], L_hand="open_up", sway=-0.012),
    "spell_raise": dict(R=[(0.150, 0.880, 0.040), (0.170, 0.985, 0.080)], R_hand="open_up",
                        L=[(-0.112, 0.680, 0.010), (-0.122, 0.570, 0.040)], L_hand="relaxed", sway=0.010),
    "hold_front": dict(R=[(0.112, 0.680, 0.060), (0.040, 0.650, 0.112)], R_hand="cup",
                       L=[(-0.112, 0.680, 0.060), (-0.040, 0.650, 0.112)], L_hand="cup", sway=0.0),
    "hip_raise": dict(R=[(0.152, 0.700, -0.020), (0.078, 0.618, 0.024)], R_hand="hip",
                      L=[(-0.140, 0.810, 0.050), (-0.150, 0.912, 0.100)], L_hand="open_up", sway=0.016),
    "weapon_plant": dict(R=[(0.132, 0.680, 0.030), (0.150, 0.600, 0.080)], R_hand="grip",
                         L=[(-0.152, 0.700, -0.020), (-0.078, 0.618, 0.024)], L_hand="hip", sway=-0.010),
    "weapon_diag": dict(R=[(0.124, 0.690, 0.060), (0.070, 0.640, 0.125)], R_hand="grip",
                        L=[(-0.110, 0.750, 0.070), (-0.040, 0.770, 0.135)], L_hand="grip", sway=0.012),
    "hand_chest": dict(R=[(0.112, 0.690, 0.060), (0.034, 0.738, 0.086)], R_hand="open",
                       L=[(-0.150, 0.700, 0.000), (-0.205, 0.620, 0.010)], L_hand="grip", sway=-0.008),
    "hair_touch": dict(R=[(0.150, 0.905, 0.000), (0.072, 0.975, -0.020)], R_hand="open",
                       L=[(-0.152, 0.700, -0.020), (-0.078, 0.618, 0.024)], L_hand="hip", sway=0.018),
    "parasol": dict(R=[(0.122, 0.690, 0.050), (0.072, 0.742, 0.090)], R_hand="grip",
                    L=[(-0.110, 0.680, 0.040), (-0.060, 0.630, 0.090)], L_hand="grip", sway=-0.010),
    "duchess": dict(R=[(0.140, 0.810, 0.050), (0.150, 0.912, 0.100)], R_hand="open_up",
                    L=[(-0.152, 0.700, -0.020), (-0.078, 0.618, 0.024)], L_hand="hip", sway=-0.016),
    "offer": dict(R=[(0.122, 0.700, 0.060), (0.075, 0.708, 0.150)], R_hand="open_up",
                  L=[(-0.122, 0.700, 0.060), (-0.075, 0.708, 0.150)], L_hand="open_up", sway=0.0),
    "hat_hold": dict(R=[(0.150, 0.880, 0.060), (0.104, 0.982, 0.080)], R_hand="grip",
                     L=[(-0.112, 0.680, 0.010), (-0.122, 0.570, 0.040)], L_hand="relaxed", sway=0.012),
    "arms_up": dict(R=[(0.150, 0.905, 0.010), (0.130, 1.030, 0.040)], R_hand="open",
                    L=[(-0.150, 0.905, 0.010), (-0.130, 1.030, 0.040)], L_hand="open", sway=0.0),
    "open_arms": dict(R=[(0.142, 0.700, 0.030), (0.205, 0.640, 0.070)], R_hand="open_up",
                      L=[(-0.142, 0.700, 0.030), (-0.205, 0.640, 0.070)], L_hand="open_up", sway=0.0),
    "heart_hold": dict(R=[(0.112, 0.680, 0.060), (0.036, 0.715, 0.104)], R_hand="cup",
                       L=[(-0.112, 0.680, 0.060), (-0.036, 0.715, 0.104)], L_hand="cup", sway=0.008),
    "scepter": dict(R=[(0.124, 0.680, 0.050), (0.092, 0.640, 0.110)], R_hand="grip",
                    L=[(-0.150, 0.700, 0.000), (-0.212, 0.630, -0.020)], L_hand="grip", sway=-0.012),
    "dream": dict(R=[(0.150, 0.865, 0.020), (0.205, 0.935, 0.060)], R_hand="open",
                  L=[(-0.132, 0.780, 0.050), (-0.190, 0.800, 0.100)], L_hand="open_up", sway=0.020),
}


def arm(d, key):
    """(shoulder, elbow, wrist) of one arm, unit coordinates."""
    p = POSES[d["pose"]]
    sx = SHOULDER if key == "R" else -SHOULDER
    return np.array([sx, 0.806, 0.0]), np.array(p[key][0]), np.array(p[key][1])


def hand_point(d, key):
    """Where the hand holds things (unit coordinates) and the forearm direction."""
    sh, el, wr = arm(d, key)
    dirv = (wr - el) / np.linalg.norm(wr - el)
    return wr + dirv * 0.016, dirv


def build_figure(B, d, s):
    """The shared adult body, standing; outfit, sleeves, skirt and hair from the design."""
    hy = head_y()
    outfit = d["outfit"]

    def chin(lon, lat):
        return 1.0 - 0.30 * max(0.0, -math.sin(lat)) ** 1.7
    B.ellipsoid((0, hy * s, 0.004 * s), (0.057 * s, 0.071 * s, 0.061 * s), "face", nu=28, nv=18, bulge=chin)
    tube(B, [(0, 0.815 * s, -0.004 * s), (0, 0.86 * s, 0.0), (0, 0.892 * s, 0.006 * s)], [0.020 * s, 0.017 * s, 0.016 * s], "skin", nu=10)
    bod = d.get("bodice", "plate" if outfit == "armor" else "gown")
    B.lathe([(0.0, 0.585), (0.050, 0.590), (0.054, 0.640), (0.064, 0.700), (0.071, 0.750), (0.074, 0.785),
             (0.068, 0.812), (0.040, 0.832), (0.0, 0.838)], bod, nu=18, squash=(1.0, 0.70), scale=s)
    sleeve = d.get("sleeve", "bracer" if outfit == "armor" else "bell")
    for side in (-1, 1):
        B.ellipsoid((side * 0.029 * s, 0.748 * s, 0.030 * s), (0.030 * s, 0.028 * s, 0.024 * s), bod, nu=12, nv=8)
        sh_reg = "skin" if sleeve == "bare" else ("plate" if outfit == "armor" else "gown2")
        B.ellipsoid((side * 0.080 * s, 0.802 * s, 0.0), (0.028 * s, 0.026 * s, 0.026 * s), sh_reg, nu=12, nv=8)
    B.lathe([(0.0, -0.008), (0.056, -0.008), (0.060, 0.0), (0.056, 0.010), (0.0, 0.010)], "trim", base=(0, 0.600 * s, 0),
            nu=22, squash=(1.0, 0.74), scale=s)
    tube(B, [(-0.064 * s, 0.808 * s, 0.020 * s), (-0.036 * s, 0.796 * s, 0.046 * s), (0.0, 0.790 * s, 0.056 * s),
             (0.036 * s, 0.796 * s, 0.046 * s), (0.064 * s, 0.808 * s, 0.020 * s)],
         [0.004 * s, 0.0045 * s, 0.005 * s, 0.0045 * s, 0.004 * s], "trim", nu=6, nv=20)
    if outfit == "armor":
        build_armor(B, d, s)
    if d.get("collar"):
        build_collar(B, d, s)
    skirt = d.get("skirt", "gown")
    if skirt == "mermaid":
        build_mermaid(B, d, s)
    elif skirt == "short":
        build_skirt(B, d, s, length=0.26)
        build_legs(B, d, s)
    else:
        build_skirt(B, d, s)
        if skirt == "tiered":
            build_skirt(B, d, s, length=0.40, region="gown", scale=1.07, panel=False, hem_lobes=True)
        elif skirt == "layered":
            build_skirt(B, d, s, length=0.50, region="gown2", scale=1.06, panel=False, hem_lobes=True)
    build_arms(B, d, s, sleeve)
    build_hair(B, d, s)


def _skirt_profile(length):
    """Radius by height for a gown whose hem is at `length` below the waist (0.604)."""
    full = [(0.0, 0.0), (0.172, 0.0), (0.168, 0.06), (0.150, 0.16), (0.126, 0.30), (0.104, 0.43), (0.090, 0.52),
            (0.064, 0.590), (0.0, 0.604)]
    if length is None:
        return full
    hem = 0.604 - length
    out = [(0.0, hem), (float(np.interp(hem, [p[1] for p in full[1:]], [p[0] for p in full[1:]])) + 0.004, hem)]
    out += [p for p in full[2:] if p[1] > hem + 0.02]
    return out


def build_skirt(B, d, s, length=None, region="gown", scale=1.0, panel=True, hem_lobes=False):
    """A gown flaring to the floor (or to `length` below the waist), soft folds, a train
    that trails back and sways with the pose. hem_lobes: a scalloped hem (over-skirts)."""
    pose = POSES[d["pose"]]
    prof = _skirt_profile(length)
    sway = pose.get("sway", 0.0)
    train = d.get("train", 0.035)
    ys = [p[1] for p in prof]
    rs = [p[0] * scale for p in prof]
    nv = 2 * (len(prof) - 1)
    hem_y = ys[0]

    def shape(lon, y, r):
        low = max(0.0, 1.0 - y / 0.55)
        r *= 1.0 + 0.055 * low * math.sin(7 * lon + 0.6) + 0.025 * low * math.sin(13 * lon)
        r *= 1.0 - 0.10 * low * max(0.0, math.cos(lon))
        x = r * math.sin(lon) + sway * low * low
        z = r * 0.88 * math.cos(lon) - train * low * low
        return x, z

    def fn(lon, lat):
        t = (lat + math.pi / 2) / math.pi
        y = _interp(ys, t)
        r = _interp(rs, t)
        if hem_lobes and t < 0.2 and r > 1e-6:      # scallops (not at the closing centre point)
            y += 0.025 * (0.5 + 0.5 * math.cos(9 * lon)) * (1 - t / 0.2)
        x, z = shape(lon, y, r)
        return (x * s, y * s, z * s)
    B.surface(fn, region, nu=32, nv=nv)
    if panel and d.get("panel", True):
        pts, radii = [], []
        for y in [v for v in (0.585, 0.50, 0.38, 0.24, 0.10, 0.03) if v > hem_y + 0.01] + [hem_y + 0.012]:
            rr = float(np.interp(y, ys[1:], rs[1:]))
            x, z = shape(0.0, y, rr)
            pts.append((x * s, y * s, (z + 0.002) * s))
            radii.append((0.018 + 0.05 * (0.6 - y)) * s)
        tube(B, pts, radii, "gown2", nu=12, depth=0.08, side=(1, 0, 0))
    if region == "gown" and scale == 1.0:
        hy0 = hem_y + 0.012
        rr = float(np.interp(hy0, ys[1:], rs[1:]))
        ring = []
        for a in np.linspace(-math.pi, math.pi, 25):
            x, z = shape(a, hy0, rr)
            ring.append((x * s, hy0 * s, z * s))
        tube(B, ring, [0.006 * s] * 25, "trim", nu=5, nv=40, caps=False)


def build_legs(B, d, s):
    """Below a mid-calf dress: legs and strappy sandals."""
    for side in (-1, 1):
        tube(B, [(side * 0.034 * s, 0.36 * s, 0.0), (side * 0.038 * s, 0.20 * s, 0.006 * s), (side * 0.040 * s, 0.035 * s, 0.004 * s)],
             [0.024 * s, 0.017 * s, 0.012 * s], "skin", nu=10)
        B.ellipsoid((side * 0.041 * s, 0.014 * s, 0.020 * s), (0.016 * s, 0.013 * s, 0.032 * s), "skin", nu=10, nv=6)
        B.ellipsoid((side * 0.041 * s, 0.006 * s, 0.020 * s), (0.018 * s, 0.006 * s, 0.035 * s), "gown2", nu=10, nv=6)
        B.lathe([(0.0, -0.004), (0.0135, -0.004), (0.0135, 0.004), (0.0, 0.004)], "gown2", base=(side * 0.040 * s, 0.050 * s, 0.004 * s),
                nu=10, scale=s)


def build_mermaid(B, d, s):
    """A mermaid gown: close to the hips and knees, then a fishtail fanning onto the base."""
    prof = [(0.0, 0.0), (0.150, 0.0), (0.130, 0.035), (0.070, 0.12), (0.058, 0.22), (0.070, 0.33), (0.088, 0.45),
            (0.090, 0.52), (0.064, 0.590), (0.0, 0.604)]
    ys = [p[1] for p in prof]
    rs = [p[0] for p in prof]
    sway = POSES[d["pose"]].get("sway", 0.0)

    def fn(lon, lat):
        t = (lat + math.pi / 2) / math.pi
        y = _interp(ys, t)
        r = _interp(rs, t)
        low = max(0.0, 1.0 - y / 0.15)
        r *= 1.0 + 0.10 * low * math.sin(8 * lon)
        x = r * math.sin(lon) + sway * (1 - y / 0.6) ** 2
        z = r * 0.85 * math.cos(lon) - 0.06 * low
        return (x * s, y * s, z * s)
    B.surface(fn, "tail", nu=30, nv=2 * (len(prof) - 1))
    # fin frills at the hem and a sash of seafoam
    for side in (-1, 1):
        tube(B, [(side * 0.02 * s, 0.03 * s, -0.10 * s), (side * 0.12 * s, 0.012 * s, -0.17 * s), (side * 0.20 * s, 0.03 * s, -0.16 * s)],
             [0.030 * s, 0.045 * s, 0.004 * s], "gown2", nu=10, depth=0.15, side=(0, 1, 0))
    tube(B, [(0.07 * s, 0.56 * s, 0.05 * s), (0.02 * s, 0.50 * s, 0.075 * s), (-0.05 * s, 0.42 * s, 0.07 * s), (-0.06 * s, 0.30 * s, 0.05 * s)],
         [0.012 * s, 0.016 * s, 0.014 * s, 0.003 * s], "gown2", nu=8, depth=0.35, side=(0, 0, 1))


def build_armor(B, d, s):
    """Breastplate trim, pauldrons and hip plates over the gown."""
    for side in (-1, 1):
        B.ellipsoid((side * 0.090 * s, 0.812 * s, 0.0), (0.040 * s, 0.028 * s, 0.036 * s), "plate",
                    rot=MW.rot_xyz(rz=side * -22), nu=14, nv=8)
        B.ellipsoid((side * 0.098 * s, 0.796 * s, 0.0), (0.038 * s, 0.022 * s, 0.034 * s), "trim",
                    rot=MW.rot_xyz(rz=side * -30), nu=14, nv=8)
    for k in range(7):          # hip plates (faulds) round the front and sides
        a = math.radians(-75 + 25 * k)
        top = np.array([0.058 * math.sin(a), 0.596, 0.058 * 0.74 * math.cos(a)])
        bot = np.array([0.098 * math.sin(a), 0.450, 0.098 * 0.80 * math.cos(a)])
        tube(B, [top * s, (top + bot) / 2 * s, bot * s], [0.018 * s, 0.022 * s, 0.020 * s], "plate", nu=8, depth=0.18,
             side=(math.sin(a), 0, math.cos(a)))
        B.ellipsoid(tuple(bot * s + np.array([math.sin(a), 0, math.cos(a)]) * 0.004 * s), (0.004 * s,) * 3, "gem", nu=6, nv=4)
    # a gem at the breastplate's centre
    B.ellipsoid((0, 0.770 * s, 0.054 * s), (0.008 * s, 0.009 * s, 0.006 * s), "gem", nu=10, nv=6)


def build_collar(B, d, s):
    """A tall gothic collar standing up behind the neck."""
    for side in (-1, 1):
        tube(B, [(side * 0.030 * s, 0.820 * s, -0.030 * s), (side * 0.058 * s, 0.880 * s, -0.040 * s), (side * 0.080 * s, 0.940 * s, -0.030 * s)],
             [0.010 * s, 0.030 * s, 0.002 * s], "gown2", nu=10, depth=0.12, side=(0, 0, 1))


def build_arms(B, d, s, sleeve):
    for key in ("R", "L"):
        sh, el, wr = [p * s for p in arm(d, key)]
        upper = "skin" if sleeve == "bare" else ("plate" if sleeve == "bracer" and d["outfit"] == "armor" and False else "gown2")
        tube(B, [sh, (sh + el) / 2, el], [0.024 * s, 0.021 * s, 0.018 * s], upper, nu=8, nv=8)
        fore = "gown2" if sleeve == "long" else "skin"
        tube(B, [el, (el + wr) / 2, wr + (wr - el) * 0.08], [0.017 * s, 0.015 * s, 0.012 * s], fore, nu=8, nv=8)
        dirv = (wr - el) / np.linalg.norm(wr - el)
        R = MW.align_y(dirv)
        if sleeve == "bell":
            B.lathe([(0.0, 0.0), (0.018, 0.0), (0.030, 0.040), (0.034, 0.055), (0.0, 0.058)], "gown2",
                    base=tuple(el + dirv * 0.004 * s), rot=R, nu=10, scale=s)
            B.lathe([(0.0, -0.002), (0.019, -0.002), (0.019, 0.004), (0.0, 0.004)], "trim", base=tuple(el + dirv * 0.004 * s),
                    rot=R, nu=10, scale=s)
        elif sleeve == "bracer":
            B.lathe([(0.0, 0.0), (0.019, 0.0), (0.020, 0.030), (0.017, 0.062), (0.0, 0.064)], "plate",
                    base=tuple(el + dirv * 0.012 * s), rot=R, nu=10, scale=s)
        elif sleeve == "long":
            B.lathe([(0.0, -0.003), (0.016, -0.003), (0.022, 0.006), (0.0, 0.008)], "trim", base=tuple(wr - dirv * 0.004 * s),
                    rot=R, nu=10, scale=s)
        if sleeve == "puff":
            B.ellipsoid(tuple(sh + (el - sh) * 0.25), (0.032 * s, 0.034 * s, 0.032 * s), "gown2", nu=12, nv=8)
        build_hand(B, d, s, key, wr, el)


def build_hand(B, d, s, key, wr, el):
    hand = POSES[d["pose"]][key + "_hand"]
    dirv = (wr - el) / np.linalg.norm(wr - el)
    c = wr + dirv * 0.016 * s
    if hand == "grip":
        B.ellipsoid(tuple(c), (0.016 * s, 0.019 * s, 0.017 * s), "skin", nu=10, nv=8)
    elif hand == "hip":
        B.ellipsoid(tuple(wr + dirv * 0.010 * s), (0.014 * s, 0.017 * s, 0.012 * s), "skin", nu=10, nv=8)
    elif hand in ("open_up", "cup"):
        fwd = np.array([dirv[0], 0.0, dirv[2] + 0.6])
        fwd = fwd / np.linalg.norm(fwd)
        up = np.cross(fwd, [1.0, 0.0, 0.0]) if abs(fwd[0]) < 0.9 else np.array([0, 1.0, 0])
        B.ellipsoid(tuple(wr + fwd * 0.016 * s), (0.015 * s, 0.008 * s, 0.022 * s), "skin", rot=MW.align_y(up), nu=10, nv=8)
    else:   # open / relaxed: a slim hand along the forearm, fingers together
        B.ellipsoid(tuple(wr + dirv * 0.020 * s), (0.013 * s, 0.024 * s, 0.008 * s), "skin", rot=MW.align_y(dirv), nu=10, nv=8)


def build_hair(B, d, s):
    hy = head_y()
    style = d.get("hair_style", "long")
    low_cap = 0.62 if style != "bob" else 0.62

    def cap(lon, lat):
        front = max(0.0, 1.0 - max(0.0, abs(lon) - 0.95) / 0.35)
        low = max(0.0, min(1.0, (low_cap - lat) / 0.28))
        return 1.07 - 0.22 * front * low
    B.ellipsoid((0, (hy + 0.006) * s, -0.002 * s), (0.059 * s, 0.073 * s, 0.062 * s), "hair", nu=26, nv=14, bulge=cap)
    # bangs (side-swept styles lean one way)
    lean0 = 0.8 if style == "side_swept" else 0.0
    for x0, lean in ((-0.040, -1), (-0.020, -0.5), (0.0, 0.2), (0.021, 0.6), (0.040, 1)):
        lean = lean + lean0
        tube(B, [(x0 * s, 0.995 * s, 0.022 * s), ((x0 + 0.004 * lean) * s, 0.972 * s, 0.054 * s),
                 ((x0 + 0.010 * lean) * s, 0.944 * s, 0.061 * s)], [0.013 * s, 0.010 * s, 0.0015 * s], "hair", nu=7, nv=8, depth=0.45,
             side=(1, 0, 0))
    # side locks framing the face
    lock_end = {"bob": 0.84, "bun": 0.86, "ponytail": 0.84}.get(style, 0.70)
    wave = 0.010 if style in ("wavy", "flowing") else 0.0
    for side in (-1, 1):
        if style == "side_swept" and side < 0:
            continue
        ys = np.linspace(0.955, lock_end, 4)
        pts = [(side * (0.050 + 0.016 * k / 3 + wave * math.sin(k * 2.2)) * s, y * s, (0.020 + 0.020 * min(k, 2) / 2) * s)
               for k, y in enumerate(ys)]
        tube(B, pts, [0.014 * s, 0.013 * s, 0.010 * s, 0.002 * s], "hair", nu=7, nv=10, depth=0.55, side=(0, 0, 1))
    if style in ("long", "wavy", "flowing", "side_swept"):
        end = {"long": 0.52, "wavy": 0.50, "flowing": 0.36, "side_swept": 0.52}[style]
        n = 6
        pts, rad = [], []
        for k in range(n):
            t = k / (n - 1)
            y = 0.985 + (end - 0.985) * t
            x = (0.008 + 0.03 * t * t) * (1 if style != "side_swept" else -1) + (wave * 1.4 * math.sin(t * 9) if wave else 0)
            if style == "flowing":
                x = 0.09 * t * t + wave * math.sin(t * 9)          # streaming out to her side
            z = -0.030 - 0.055 * min(1, t * 2.2) + (0.012 * t if style == "flowing" else 0)
            if style == "side_swept":   # gathered over her right shoulder, down the front
                x = -(0.02 + 0.07 * min(1, t * 2.0))
                z = -0.03 - 0.05 * math.sin(math.pi * min(1, t * 1.6)) + 0.09 * max(0, t - 0.45)
            pts.append((x * s, y * s, z * s))
            rad.append((0.052 + 0.022 * math.sin(math.pi * min(1, t * 1.3))) * (1 - 0.9 * t ** 3) * s + 0.002 * s)
        tube(B, pts, rad, "hair", nu=10, nv=16, depth=0.42 if style != "side_swept" else 0.5, side=(1, 0, 0) if style != "side_swept" else (0.5, 0, 1))
    elif style == "ponytail":
        tie = np.array([0.0, 1.000, -0.056])
        B.ellipsoid(tuple(tie * s), (0.012 * s,) * 3, "gown2", nu=8, nv=6)
        pts = [tie, tie + [0.006, -0.015, -0.030], tie + [0.014, -0.070, -0.042], tie + [0.024, -0.180, -0.036], tie + [0.036, -0.300, -0.020]]
        tube(B, [np.array(p) * s for p in pts], [0.016 * s, 0.024 * s, 0.026 * s, 0.020 * s, 0.003 * s], "hair", nu=10, nv=16)
    elif style == "bun":
        B.ellipsoid((0, 0.990 * s, -0.058 * s), (0.036 * s, 0.032 * s, 0.030 * s), "hair", nu=14, nv=10)
        B.lathe([(0.0, -0.004), (0.030, -0.004), (0.031, 0.0), (0.030, 0.004), (0.0, 0.004)], "trim", base=(0, 0.990 * s, -0.050 * s),
                rot=MW.rot_xyz(rx=70), nu=14, scale=s)
    elif style == "bob":
        # a chin-length bob: fuller at the sides and back
        B.ellipsoid((0, (hy - 0.025) * s, -0.010 * s), (0.066 * s, 0.052 * s, 0.060 * s), "hair", nu=20, nv=10,
                    bulge=lambda lon, lat: 1.0 - 0.35 * max(0.0, 1.0 - max(0.0, abs(lon) - 0.7) / 0.4))
    elif style == "braid":
        # a long braid over her left shoulder (+x), down the front
        pts = [np.array(p) for p in ((0.045, 0.94, -0.030), (0.075, 0.86, 0.010), (0.080, 0.76, 0.050), (0.070, 0.62, 0.060), (0.060, 0.52, 0.058))]
        for k in range(14):
            t = k / 13
            c = _catmull(pts, t)
            r = 0.020 - 0.008 * t
            B.ellipsoid(tuple(c * s + np.array([0.004 * (1 if k % 2 else -1), 0, 0]) * s), (r * s, r * 0.9 * s, r * 0.8 * s), "hair", nu=10, nv=6)
        B.ellipsoid(tuple(pts[-1] * s - np.array([0, 0.012, 0]) * s), (0.010 * s,) * 3, "trim", nu=8, nv=6)
        tube(B, [(0, 0.985 * s, -0.030 * s), (0.0, 0.90 * s, -0.062 * s), (0.0, 0.82 * s, -0.066 * s)],
             [0.050 * s, 0.060 * s, 0.004 * s], "hair", nu=10, nv=10, depth=0.42, side=(1, 0, 0))


# =========================================================================== props
# Every prop is prop_<name>(B, d, s). Positions are unit coordinates x s.
HEAD_TOP = 1.003     # top of the hair cap
BROW = 0.958         # where a circlet / crown band sits


def _v(*a):
    return np.array(a, dtype=float)


def held_orb(B, c, r, s, region="gem", ring=False):
    B.ellipsoid(tuple(c * s), (r * s,) * 3, region, nu=16, nv=12)
    B.ellipsoid(tuple((c + _v(r * 0.3, r * 0.3, r * 0.65)) * s), (r * 0.33 * s,) * 3, "gemcore", nu=8, nv=6)
    if ring:
        pts = [(c + r * 1.65 * _v(math.cos(a), 0.30 * math.sin(a), math.sin(a))) * s for a in np.linspace(0, TAU, 25)]
        tube(B, pts, [0.0022 * s] * 25, "trim", nu=4, nv=36, caps=False)


def faceted(B, c, r, h, region, s, axis=(0, 1, 0), nu=6):
    """A cut gem / crystal: a double cone."""
    R = MW.align_y(axis)
    B.lathe([(0.0, -h * 0.45), (r, 0.0), (r * 0.8, h * 0.15), (0.0, h * 0.55)], region, base=tuple(c * s), rot=R, nu=nu, scale=s)


def rose(B, c, r, s, region="gem", centre="gemcore", facing=(0, 0, 1)):
    """A small rose: a bud and five cupped petals."""
    f = _v(*facing)
    f = f / np.linalg.norm(f)
    R = MW.align_y(f)
    B.ellipsoid(tuple(c * s), (r * 0.55 * s, r * 0.5 * s, r * 0.55 * s), centre, rot=R, nu=10, nv=6)
    for k in range(5):
        a = TAU * k / 5
        off = R @ _v(math.cos(a) * r * 0.55, -r * 0.1, math.sin(a) * r * 0.55)
        B.ellipsoid(tuple(c * s + off * s), (r * 0.45 * s, r * 0.30 * s, r * 0.45 * s), region, rot=R, nu=8, nv=5)


def heart(B, c, r, s, region="gem", facing=(0, 0, 1)):
    """A puffy heart: two lobes and a point."""
    for side in (-1, 1):
        B.ellipsoid(tuple((c + _v(side * r * 0.5, r * 0.25, 0)) * s), (r * 0.55 * s, r * 0.55 * s, r * 0.40 * s), region, nu=12, nv=8)
    B.lathe([(0.0, 0.0), (r * 0.95, r * 0.75), (0.0, r * 0.95)], region, base=tuple((c + _v(0, -r * 0.9, 0)) * s), nu=12,
            squash=(1.0, 0.42), scale=s)


def circlet(B, d, s, region="trim", y=BROW, r=0.066, tilt=10, thick=0.004):
    pts = [_v(r * math.sin(a), y + 0.012 * math.cos(a) * math.sin(math.radians(tilt)) * 5, r * 0.94 * math.cos(a) - 0.004)
           for a in np.linspace(-math.pi, math.pi, 25)]
    tube(B, [p * s for p in pts], [thick * s] * 25, region, nu=5, nv=40, caps=False)
    return _v(0, y + 0.012 * math.sin(math.radians(tilt)) * 5, r * 0.94 - 0.004)


def prop_witch_hat(B, d, s):
    hy = head_y()
    tilt = MW.rot_xyz(rz=-12, rx=-8)
    base = np.array([0.006, hy + 0.040, -0.006]) * s
    B.lathe([(0.0, -0.004), (0.112, -0.004), (0.118, 0.0), (0.110, 0.004), (0.0, 0.006)], "gown", base=tuple(base), rot=tilt,
            nu=28, scale=s)
    up = tilt @ np.array([0, 1, 0])
    back = tilt @ np.array([0, 0, -1])
    pts = [base + up * 0.004 * s, base + up * 0.060 * s, base + (up * 0.110 + back * 0.020) * s, base + (up * 0.150 + back * 0.065) * s]
    tube(B, pts, [0.060 * s, 0.042 * s, 0.020 * s, 0.002 * s], "gown", nu=16, nv=20)
    B.lathe([(0.0, 0.0), (0.0605, 0.0), (0.0575, 0.014), (0.0, 0.014)], "gown2", base=tuple(base + up * 0.004 * s), rot=tilt, nu=20,
            scale=s)
    crescent(B, base + (up * 0.012 + tilt @ np.array([0.0, 0, 0.060])) * s, 0.011 * s, 0.006 * s, "trim",
             normal=tilt @ np.array([0, 0, 1.0]), up=(1, 1, 0))


def _staff(B, d, s, key="R", top_y=1.06, bottom_y=0.0, region="staff", r=0.0075, tilt=(0.006, 0.006)):
    g, dirv = hand_point(d, key)
    bottom = _v(g[0] - tilt[0] * 0.6, bottom_y, g[2] - tilt[1] * 0.6)
    top = _v(g[0] + tilt[0], top_y, g[2] + tilt[1])
    tube(B, [bottom * s, (bottom + top) / 2 * s, top * s], [r * s, r * 0.93 * s, r * 0.87 * s], region, nu=8)
    return bottom, top


def prop_crescent_staff(B, d, s):
    bottom, top = _staff(B, d, s)
    for y in (0.35, 0.70, 0.95):
        c = bottom + (top - bottom) * y
        B.lathe([(0.0, -0.006), (0.010, -0.006), (0.011, 0.0), (0.010, 0.006), (0.0, 0.006)], "trim", base=tuple(c * s), nu=10, scale=s)
    head = (top + _v(0, 0.055, 0)) * s
    crescent(B, head, 0.055 * s, 0.018 * s, "trim", normal=(0, 0, 1), up=(0.45, 1, 0), open_deg=95)
    B.ellipsoid(tuple(head), (0.018 * s,) * 3, "gem", nu=14, nv=10)
    B.ellipsoid(tuple(head + _v(0.005, 0.005, 0.012) * s), (0.006 * s,) * 3, "gemcore", nu=8, nv=6)
    star4(B, head + _v(0.05, 0.06, 0.0) * s, 0.016 * s, "gemcore")
    star4(B, head + _v(-0.055, 0.01, 0.01) * s, 0.011 * s, "gemcore")


def prop_moon_orb(B, d, s):
    g, _ = hand_point(d, "L")
    held_orb(B, g + _v(0.0, 0.026, 0.006), 0.024, s, ring=True)


def prop_cape(B, d, s, region="cape", spread=0.0, wide=1.0, held=None):
    """A long cape from the shoulders to the floor. held = "L": its left edge is held out."""
    pts = [(0, 0.815, -0.050), (0, 0.620, -0.110), (-0.006, 0.360, -0.150), (-0.012, 0.120, -0.200), (-0.016, 0.022, -0.236)]
    tube(B, [_v(*p) * s for p in pts], [r * wide * s for r in (0.082, 0.120, 0.150, 0.170, 0.170)], region, nu=18, depth=0.10,
         side=(1, 0, 0), caps=True)
    tube(B, [_v(-0.090, 0.818, -0.020) * s, _v(0.0, 0.826, -0.060) * s, _v(0.090, 0.818, -0.020) * s], [0.010 * s] * 3, "trim", nu=8, nv=16)
    if held:
        g, _ = hand_point(d, held)
        sx = 1 if held == "R" else -1
        swing = [_v(sx * 0.070, 0.805, -0.040), (g + _v(sx * 0.02, 0.0, -0.040)), _v(g[0] + sx * 0.05, 0.30, -0.10),
                 _v(g[0] + sx * 0.06, 0.03, -0.14)]
        tube(B, [p * s for p in swing], [0.030 * s, 0.050 * s, 0.075 * s, 0.085 * s], region, nu=14, depth=0.10, side=(0, 0, 1))


def prop_rose_magic(B, d, s):
    g, _ = hand_point(d, "R")
    for k in range(7):          # a spiral of roses rising from her raised hand
        t = k / 6
        a = TAU * 1.2 * t
        c = g + _v(0.045 * math.cos(a) * (1 - 0.4 * t), 0.02 + 0.13 * t, 0.045 * math.sin(a) * (1 - 0.4 * t) + 0.01)
        rose(B, c, 0.016 - 0.005 * t, s, facing=(math.cos(a), 0.6, math.sin(a) + 0.5))
    for k in range(4):
        star4(B, (g + _v(0.06 * math.cos(k * 1.7), 0.06 + 0.04 * k, 0.05 * math.sin(k * 1.7))) * s, 0.009 * s, "gemcore")
    rose(B, _v(0.055, 0.985, 0.020), 0.017, s, facing=(0.6, 0.3, 0.8))     # a rose in her hair


def prop_crystal_crown(B, d, s):
    c = circlet(B, d, s, "trim")
    for k, (a, h) in enumerate(((-50, 0.040), (-25, 0.055), (0, 0.075), (25, 0.055), (50, 0.040))):
        a = math.radians(a)
        p = _v(0.064 * math.sin(a), BROW + 0.004, 0.060 * math.cos(a) - 0.004)
        faceted(B, p + _v(0, h * 0.4, 0), 0.010, h, "gem", s, axis=(math.sin(a) * 0.3, 1, math.cos(a) * 0.2), nu=5)


def prop_ice_orb(B, d, s):
    a, _ = hand_point(d, "R")
    b, _ = hand_point(d, "L")
    c = (a + b) / 2 + _v(0, 0.040, 0.010)
    held_orb(B, c, 0.032, s)
    for k in range(5):
        faceted(B, c + _v(0.055 * math.cos(k * 1.26), 0.03 * math.sin(k * 2.0), 0.040 * math.sin(k * 1.26)), 0.006, 0.020, "gemcore", s,
                axis=(math.cos(k), 1, math.sin(k)), nu=4)


def prop_gold_circlet(B, d, s):
    front = circlet(B, d, s, "gold")
    faceted(B, front + _v(0, -0.002, 0.004), 0.008, 0.018, "gem", s, axis=(0, 0, 1))
    pearls = [_v(0.060 * math.sin(a), 0.792 - 0.012 * math.cos(a), 0.047 * math.cos(a) + 0.006) for a in np.linspace(-1.1, 1.1, 13)]
    for p in pearls:                      # a gold collar necklace
        B.ellipsoid(tuple(p * s), (0.0045 * s,) * 3, "gold", nu=8, nv=5)
    faceted(B, _v(0, 0.770, 0.060), 0.009, 0.020, "gem", s, axis=(0, 0, 1))


def prop_emerald(B, d, s):
    g, _ = hand_point(d, "L")
    c = g + _v(0, 0.050, 0.004)
    faceted(B, c, 0.020, 0.050, "gem", s, nu=6)
    for k in range(3):
        star4(B, (c + _v(0.035 * math.cos(k * 2.1), 0.02 * k, 0.03 * math.sin(k * 2.1))) * s, 0.008 * s, "gemcore")


def _wing(B, root, side, s, n=7, length=0.30, spread=(-15, 80), region="feather", tip_r=0.002, width=0.030, back=0.6, droop=0.0):
    """A wing of feathers (or blades) fanning from `root` out to `side` (+1/-1) and up."""
    for k in range(n):
        t = k / max(1, n - 1)
        ang = math.radians(spread[0] + (spread[1] - spread[0]) * t)
        L = length * (1.0 - 0.45 * t)
        direction = _v(side * math.cos(ang), math.sin(ang), -back * 0.35)
        direction = direction / np.linalg.norm(direction)
        mid = root + direction * L * 0.5 + _v(0, -droop * L * 0.2, 0)
        tip = root + direction * L
        tube(B, [root * s, mid * s, tip * s], [width * 0.6 * s, width * s, tip_r * s], region, nu=6, nv=8, depth=0.18,
             side=np.cross(_v(0, 0, 1), direction))


def prop_wings_feather(B, d, s, scale=1.0):
    for side in (-1, 1):
        root = _v(side * 0.035, 0.780, -0.070)
        _wing(B, root, side, s, n=7, length=0.33 * scale, spread=(-25, 75), width=0.034 * scale)
        _wing(B, root + _v(0, 0.01, 0.006), side, s, n=5, length=0.18 * scale, spread=(-5, 55), width=0.030 * scale, region="feather2")


def prop_small_wings(B, d, s):
    prop_wings_feather(B, d, s, scale=0.62)


def prop_winged_helm(B, d, s):
    front = circlet(B, d, s, "gold", thick=0.005)
    faceted(B, front, 0.007, 0.016, "gem", s, axis=(0, 0, 1))
    for side in (-1, 1):
        root = _v(side * 0.064, BROW + 0.008, 0.0)
        for k in range(3):
            ang = math.radians(25 + 22 * k)
            tip = root + _v(side * math.cos(ang) * (0.06 - 0.012 * k), math.sin(ang) * (0.06 - 0.012 * k), -0.03)
            tube(B, [root * s, (root + tip) / 2 * s, tip * s], [0.006 * s, 0.009 * s, 0.003 * s], "gold", nu=6, nv=6, depth=0.25,
                 side=np.cross(_v(0, 0, 1), tip - root))


def prop_sword(B, d, s):
    g, _ = hand_point(d, "R")
    top = g + _v(0, 0.075, 0)
    guard = g - _v(0, 0.030, 0)
    tip = _v(g[0], 0.004, g[2])
    tube(B, [guard * s, ((guard + tip) / 2) * s, tip * s], [0.014 * s, 0.012 * s, 0.001 * s], "blade", nu=6, nv=8, depth=0.22,
         side=(1, 0, 0))
    tube(B, [(guard + _v(-0.045, 0.004, 0)) * s, guard * s, (guard + _v(0.045, 0.004, 0)) * s], [0.006 * s, 0.008 * s, 0.006 * s], "gold",
         nu=6, nv=10)
    tube(B, [guard * s, top * s], [0.006 * s, 0.006 * s], "gown2", nu=6, nv=4)
    B.ellipsoid(tuple(top * s), (0.010 * s,) * 3, "gem", nu=10, nv=6)


def prop_thorn_crown(B, d, s):
    circlet(B, d, s, "trim", thick=0.005)
    for k in range(9):
        a = math.radians(-100 + 25 * k)
        p = _v(0.065 * math.sin(a), BROW + 0.004, 0.061 * math.cos(a) - 0.004)
        h = 0.040 if k % 2 == 0 else 0.026
        tube(B, [p * s, (p + _v(0.004 * math.sin(a), h * 0.6, 0.004 * math.cos(a))) * s, (p + _v(0.010 * math.sin(a), h, 0.006 * math.cos(a))) * s],
             [0.006 * s, 0.004 * s, 0.0008 * s], "dark" if k % 2 else "trim", nu=5, nv=6)
    faceted(B, _v(0, BROW + 0.012, 0.064), 0.008, 0.020, "gem", s, axis=(0, 0.3, 1))


def prop_scepter(B, d, s):
    g, _ = hand_point(d, "R")
    bottom, top = g - _v(0, 0.10, 0), g + _v(0.004, 0.17, 0.004)
    tube(B, [bottom * s, top * s], [0.006 * s, 0.006 * s], "trim", nu=6, nv=4)
    B.ellipsoid(tuple(bottom * s), (0.008 * s,) * 3, "trim", nu=8, nv=6)
    crescent(B, (top + _v(0, 0.024, 0)) * s, 0.024 * s, 0.007 * s, "trim", normal=(0, 0, 1), up=(0, 1, 0), open_deg=120)
    faceted(B, top + _v(0, 0.026, 0), 0.012, 0.034, "gem", s)


def prop_star_scepter(B, d, s):
    g, _ = hand_point(d, "R")
    bottom, top = g - _v(0, 0.10, 0), g + _v(0.004, 0.19, 0.004)
    tube(B, [bottom * s, top * s], [0.006 * s, 0.006 * s], "trim", nu=6, nv=4)
    star4(B, (top + _v(0, 0.03, 0)) * s, 0.034 * s, "gem", depth=0.5)
    held_orb(B, top + _v(0, 0.03, 0.002), 0.010, s)


def prop_spear(B, d, s, trident=False):
    a, _ = hand_point(d, "R")
    if POSES[d["pose"]]["L_hand"] == "grip" and not trident:
        b, _ = hand_point(d, "L")
        axis = (b - a) / np.linalg.norm(b - a)
        start, end = a - axis * 0.32, b + axis * 0.42
    else:
        axis = _v(0.02, 1.0, 0.02)
        axis = axis / np.linalg.norm(axis)
        start, end = _v(a[0], 0.004, a[2]), a + axis * (1.10 - a[1])
    tube(B, [start * s, (start + end) / 2 * s, end * s], [0.0065 * s] * 3, "staff", nu=6, nv=6)
    if trident:
        side = np.cross(axis, _v(0, 0, 1))
        side = side / np.linalg.norm(side)
        B.lathe([(0.0, -0.004), (0.012, -0.004), (0.013, 0.006), (0.0, 0.008)], "trim", base=tuple(end * s), rot=MW.align_y(axis), nu=8, scale=s)
        for k in (-1, 0, 1):
            root = end + side * 0.026 * k
            tip = root + axis * (0.075 if k == 0 else 0.060)
            mid = (end + axis * 0.035) if k == 0 else (root + axis * 0.012)
            tube(B, [(end + axis * 0.002) * s, mid * s, tip * s], [0.004 * s, 0.005 * s, 0.0008 * s], "trim", nu=5, nv=8)
            faceted(B, tip - axis * 0.006, 0.008, 0.020, "trim", s, axis=axis, nu=4)
        faceted(B, end + axis * 0.010, 0.007, 0.016, "gem", s, axis=(0, 0, 1))
    else:
        tube(B, [end * s, (end + axis * 0.045) * s, (end + axis * 0.095) * s], [0.016 * s, 0.014 * s, 0.0008 * s], "blade", nu=6, nv=8,
             depth=0.22, side=np.cross(axis, _v(0, 0, 1)))
        B.lathe([(0.0, -0.005), (0.011, -0.005), (0.012, 0.005), (0.0, 0.006)], "gold", base=tuple(end * s), rot=MW.align_y(axis), nu=8,
                scale=s)
        tube(B, [end * s, (end - axis * 0.03 + _v(0.012, -0.03, 0.01)) * s, (end - axis * 0.06 + _v(0.02, -0.07, 0.02)) * s],
             [0.006 * s, 0.010 * s, 0.002 * s], "gem", nu=6, nv=8)     # a flame-red tassel


def prop_trident(B, d, s):
    prop_spear(B, d, s, trident=True)


def prop_batwing_cape(B, d, s):
    prop_cape(B, d, s, region="gown2", held="L")
    # scalloped bat-wing hem: points along the bottom edge
    for k in range(6):
        x = -0.15 + 0.06 * k
        tube(B, [_v(x, 0.05, -0.215) * s, _v(x + 0.015, 0.020, -0.22) * s, _v(x + 0.03, 0.004, -0.225) * s],
             [0.020 * s, 0.014 * s, 0.004 * s], "gown2", nu=6, nv=6, depth=0.25, side=(0, 0, 1))
    B.lathe([(0.0, -0.004), (0.020, -0.004), (0.020, 0.004), (0.0, 0.004)], "gown2", base=(0, 0.862 * s, 0.004 * s), nu=12, scale=s)
    faceted(B, _v(0, 0.850, 0.022), 0.006, 0.014, "gem", s, axis=(0, 0, 1))


def prop_horns_small(B, d, s):
    for side in (-1, 1):
        root = _v(side * 0.032, 0.990, 0.020)
        pts = [root, root + _v(side * 0.010, 0.025, -0.010), root + _v(side * 0.020, 0.044, -0.030), root + _v(side * 0.018, 0.052, -0.050)]
        tube(B, [p * s for p in pts], [0.010 * s, 0.008 * s, 0.005 * s, 0.0008 * s], "dark", nu=8, nv=10)


def prop_horns_curved(B, d, s):
    for side in (-1, 1):
        root = _v(side * 0.045, 0.985, 0.005)
        pts = [root]
        for k in range(1, 9):
            a = k * 0.62
            pts.append(root + _v(side * (0.030 + 0.020 * math.sin(a * 0.6)) * min(1, k / 3), 0.035 * math.sin(a * 0.9) + 0.008 * k * 0.4,
                                 -0.034 * (1 - math.cos(a * 0.8))))
        rad = [0.012 * (1 - 0.88 * k / 8) + 0.0006 for k in range(9)]
        tube(B, [p * s for p in pts], [r * s for r in rad], "dark", nu=8, nv=24)


def prop_wings_bat(B, d, s):
    for side in (-1, 1):
        root = _v(side * 0.030, 0.770, -0.065)
        _wing(B, root, side, s, n=4, length=0.20, spread=(-10, 70), region="gown2", width=0.040, back=0.4)
        for k in range(4):     # dark ribs along each panel
            ang = math.radians(-10 + 80 * k / 3)
            tip = root + _v(side * math.cos(ang), math.sin(ang), -0.14) * 0.20 * (1 - 0.45 * k / 3)
            tube(B, [root * s, tip * s], [0.004 * s, 0.0008 * s], "dark", nu=5, nv=4)


def prop_parasol(B, d, s):
    g, _ = hand_point(d, "R")
    axis = _v(0.25, 1.0, -0.45)
    axis = axis / np.linalg.norm(axis)
    bottom = g - axis * 0.10
    top = g + axis * 0.30
    tube(B, [bottom * s, top * s], [0.004 * s, 0.004 * s], "dark", nu=6, nv=4)
    B.ellipsoid(tuple(bottom * s), (0.007 * s,) * 3, "trim", nu=8, nv=6)
    R = MW.align_y(axis)
    B.lathe([(0.0, -0.002), (0.060, -0.005), (0.104, -0.013), (0.111, -0.010), (0.106, -0.003), (0.090, 0.008), (0.050, 0.026), (0.0, 0.034)],
            "lace", base=tuple((top - axis * 0.03) * s), rot=R, nu=8, scale=s * 1.15)
    rim = [(top - axis * 0.03) * s + (R @ _v(0.126 * math.sin(a), -0.013, 0.126 * math.cos(a))) * s for a in np.linspace(0, TAU, 17)]
    tube(B, rim, [0.004 * s] * 17, "trim", nu=4, nv=32, caps=False)
    B.ellipsoid(tuple((top + axis * 0.012) * s), (0.006 * s,) * 3, "trim", nu=8, nv=6)


def prop_black_rose(B, d, s):
    g, _ = hand_point(d, "L")
    tube(B, [(g - _v(0, 0.05, 0)) * s, (g + _v(0, 0.03, 0.02)) * s], [0.0025 * s, 0.002 * s], "leaf", nu=5, nv=4)
    rose(B, g + _v(0, 0.045, 0.026), 0.020, s, region="dark", centre="gem", facing=(0, 0.5, 1))
    rose(B, _v(-0.058, 0.975, 0.018), 0.018, s, region="dark", centre="gem", facing=(-0.6, 0.3, 0.8))


def prop_dark_orb(B, d, s):
    g, _ = hand_point(d, "R")
    c = g + _v(0, 0.040, 0.006)
    held_orb(B, c, 0.026, s)
    for k in range(5):      # flames licking up round it
        a = TAU * k / 5
        root = c + _v(0.022 * math.cos(a), -0.010, 0.022 * math.sin(a))
        tube(B, [root * s, (root + _v(0.006 * math.cos(a), 0.030, 0.006 * math.sin(a))) * s, (root + _v(0, 0.060, 0)) * s],
             [0.008 * s, 0.006 * s, 0.0008 * s], "gemcore", nu=5, nv=6)


def prop_pearls(B, d, s):
    for a in np.linspace(-1.1, 1.1, 15):
        B.ellipsoid((0.060 * math.sin(a) * s, (0.795 - 0.016 * math.cos(a)) * s, (0.047 * math.cos(a) + 0.007) * s), (0.0045 * s,) * 3,
                    "pearl", nu=8, nv=5)
    a, _ = hand_point(d, "R")
    b, _ = hand_point(d, "L")
    held_orb(B, (a + b) / 2 + _v(0, 0.028, 0.0), 0.022, s, region="pearl")
    shell(B, (a + b) / 2 + _v(0, 0.006, 0.0), 0.040, s, facing=(0, 1, 0.2))


def shell(B, c, r, s, facing=(0, 0, 1), region="pearl"):
    """A scallop shell: ribs fanning from a hinge."""
    f = _v(*facing)
    f = f / np.linalg.norm(f)
    R = MW.align_y(f)
    for k in range(7):
        a = math.radians(-70 + 140 * k / 6)
        tip = R @ _v(r * math.sin(a), 0.002, r * math.cos(a))
        tube(B, [c * s, (c + tip * 0.55 + R @ _v(0, 0.004, 0)) * s, (c + tip) * s], [0.003 * s, r * 0.20 * s, r * 0.12 * s], region,
             nu=6, nv=6, depth=0.35, side=R @ _v(0, 1, 0))


def prop_shell_crown(B, d, s):
    circlet(B, d, s, "pearl", thick=0.004)
    shell(B, _v(0, BROW + 0.012, 0.050), 0.040, s, facing=(0, 0.25, 1))
    for side in (-1, 1):
        shell(B, _v(side * 0.050, BROW + 0.008, 0.030), 0.022, s, facing=(side * 0.6, 0.3, 0.8))
    for a in np.linspace(-0.9, 0.9, 9):
        B.ellipsoid((0.062 * math.sin(a) * s, 0.790 * s, (0.046 * math.cos(a) + 0.007) * s), (0.0042 * s,) * 3, "pearl", nu=8, nv=5)


def prop_sun_hat(B, d, s):
    hy = head_y()
    tilt = MW.rot_xyz(rz=10, rx=-12)
    base = _v(-0.004, hy + 0.040, 0.004) * s
    B.lathe([(0.0, -0.003), (0.125, -0.006), (0.130, -0.003), (0.122, 0.002), (0.0, 0.004)], "straw", base=tuple(base), rot=tilt, nu=28, scale=s)
    B.lathe([(0.0, 0.0), (0.062, 0.0), (0.060, 0.030), (0.045, 0.048), (0.0, 0.052)], "straw", base=tuple(base), rot=tilt, nu=20, scale=s)
    B.lathe([(0.0, 0.002), (0.0625, 0.002), (0.0615, 0.016), (0.0, 0.016)], "gown2", base=tuple(base), rot=tilt, nu=20, scale=s)
    tube(B, [base + tilt @ _v(0.04, 0.010, -0.045) * s, base + tilt @ _v(0.07, -0.03, -0.075) * s, base + tilt @ _v(0.08, -0.09, -0.09) * s],
         [0.010 * s, 0.009 * s, 0.002 * s], "gown2", nu=6, nv=8, depth=0.2, side=(0, 0, 1))
    rose(B, (base / s) + tilt @ _v(0.050, 0.012, 0.040), 0.012, s, region="gown2", centre="gem")


def prop_sun_diadem(B, d, s):
    front = circlet(B, d, s, "gold")
    for k in range(7):
        a = math.radians(-60 + 20 * k)
        L = 0.030 if k == 3 else (0.022 if k in (2, 4) else 0.015)
        p = _v(0.064 * math.sin(a), BROW + 0.006, 0.060 * math.cos(a) - 0.004)
        faceted(B, p + _v(0, L * 0.4, 0), 0.005, L, "gold", s, axis=(math.sin(a) * 0.5, 1, math.cos(a) * 0.3), nu=4)
    faceted(B, front + _v(0, 0.002, 0.003), 0.008, 0.018, "gem", s, axis=(0, 0, 1))


def prop_sun_disc(B, d, s):
    a, _ = hand_point(d, "R")
    b, _ = hand_point(d, "L")
    c = (a + b) / 2 + _v(0, 0.060, -0.010)
    B.lathe([(0.0, -0.006), (0.045, -0.006), (0.048, 0.0), (0.045, 0.006), (0.0, 0.006)], "gold", base=tuple(c * s),
            rot=MW.rot_xyz(rx=90), nu=24, scale=s)
    B.ellipsoid(tuple((c + _v(0, 0, 0.006)) * s), (0.030 * s, 0.030 * s, 0.006 * s), "gem", nu=16, nv=8)
    for k in range(12):
        ang = TAU * k / 12
        L = 0.040 if k % 2 == 0 else 0.026
        root = c + _v(0.048 * math.cos(ang), 0.048 * math.sin(ang), 0)
        faceted(B, root + _v(math.cos(ang), math.sin(ang), 0) * L * 0.45, 0.007, L, "gold", s, axis=(math.cos(ang), math.sin(ang), 0), nu=4)


def prop_star_halo(B, d, s):
    c = _v(0, 0.950, -0.075)
    ring = [(c + _v(0.110 * math.cos(a), 0.110 * math.sin(a), 0)) * s for a in np.linspace(0, TAU, 33)]
    tube(B, ring, [0.0045 * s] * 33, "gold", nu=5, nv=48, caps=False)
    for k in range(12):
        a = TAU * k / 12
        star4(B, (c + _v(0.110 * math.cos(a), 0.110 * math.sin(a), 0.004)) * s, (0.026 if k % 3 == 0 else 0.016) * s, "gemcore", depth=0.5)
    circlet(B, d, s, "gold", thick=0.0035)


def prop_hearts(B, d, s):
    a, _ = hand_point(d, "R")
    b, _ = hand_point(d, "L")
    heart(B, (a + b) / 2 + _v(0, 0.030, 0.012), 0.030, s)
    for k, (x, y, z, r) in enumerate(((0.13, 0.95, 0.04, 0.014), (-0.14, 1.02, 0.02, 0.012), (0.10, 1.10, -0.02, 0.010))):
        heart(B, _v(x, y, z), r, s, region="gemcore")
    for a2 in np.linspace(-0.6, 0.6, 7):     # a heart pendant necklace
        B.ellipsoid((0.058 * math.sin(a2) * s, (0.796 - 0.014 * math.cos(a2)) * s, (0.046 * math.cos(a2) + 0.007) * s), (0.003 * s,) * 3,
                    "gold", nu=6, nv=4)
    heart(B, _v(0, 0.770, 0.060), 0.009, s)


def prop_galaxy_cape(B, d, s):
    prop_cape(B, d, s, region="galaxy", wide=1.15, held="L")


def prop_regent_crown(B, d, s):
    hy = head_y()
    B.lathe([(0.0, 0.0), (0.050, 0.0), (0.052, 0.018), (0.050, 0.020), (0.0, 0.020)], "trim", base=(0, (HEAD_TOP - 0.020) * s, -0.004 * s),
            nu=20, scale=s)
    for k in range(7):
        a = TAU * k / 7
        p = _v(0.050 * math.sin(a), HEAD_TOP - 0.002, 0.050 * math.cos(a) - 0.004)
        faceted(B, p + _v(0, 0.014, 0), 0.008, 0.034, "trim", s, axis=(math.sin(a) * 0.2, 1, math.cos(a) * 0.2), nu=4)
        B.ellipsoid(tuple((p + _v(0, -0.008, 0)) * s), (0.004 * s,) * 3, "gem", nu=6, nv=4)


def prop_wings_crystal(B, d, s):
    for side in (-1, 1):
        root = _v(side * 0.030, 0.780, -0.070)
        for k in range(6):
            ang = math.radians(-20 + 18 * k)
            L = 0.32 * (1 - 0.10 * abs(k - 2.5))
            direction = _v(side * math.cos(ang), math.sin(ang), -0.25)
            direction = direction / np.linalg.norm(direction)
            faceted(B, root + direction * L * 0.5, 0.020, L, "crystal", s, axis=direction, nu=4)
    prop_floating_crystals(B, d, s)


def prop_floating_crystals(B, d, s):
    for k, (x, y, z, h) in enumerate(((0.18, 0.55, 0.06, 0.05), (-0.20, 0.42, 0.04, 0.04), (0.16, 1.08, -0.04, 0.035),
                                      (-0.17, 0.98, 0.0, 0.03))):
        faceted(B, _v(x, y, z), h * 0.32, h, "crystal", s, axis=(0.2 * k - 0.3, 1, 0.1), nu=5)


PROPS = {name[5:]: fn for name, fn in list(globals().items()) if name.startswith("prop_") and callable(fn)}


# =========================================================================== bases
def build_base(B, d):
    """Rarity decides the plinth. Common: a round disc. Uncommon: a disc with a metal
    rim. Rare: two round tiers. Epic: an octagonal two-tier base with trim and a name
    plate. Legendary: three tiers and a name plate. Returns the height of the top (m)."""
    r = d["rarity"]
    if r == "Common":
        B.disc_base(0.080, 0.016, "base_top", "base_side")
        return 0.016
    if r == "Uncommon":
        B.disc_base(0.084, 0.006, "base_trim", "base_trim")
        B.disc_base(0.080, 0.014, "base_top", "base_side", y0=0.006)
        return 0.020
    if r == "Rare":
        B.disc_base(0.092, 0.012, "base_trim", "base_side")
        B.disc_base(0.082, 0.014, "base_top", "base_side", y0=0.012)
        return 0.026
    oct_ = MW.rot_xyz(ry=22.5)
    big = 0.104 if r == "Epic" else 0.112
    B.lathe([(0.0, 0.0), (big, 0.0), (big, 0.010), (big - 0.006, 0.014), (0.0, 0.014)], "base_side", nu=8, rot=oct_)
    B.lathe([(0.0, 0.0), (big - 0.008, 0.0), (big - 0.006, 0.004), (big - 0.008, 0.008), (0.0, 0.008)], "base_trim", base=(0, 0.014, 0),
            nu=8, rot=oct_)
    B.disc_base(big - 0.018, 0.012, "base_top", "base_side", y0=0.022)
    top = 0.034
    if r == "Legendary":
        B.disc_base(big - 0.004, 0.004, "base_trim", "base_trim", y0=top - 0.001)
        B.disc_base(big - 0.030, 0.012, "base_top", "base_trim", y0=top + 0.003)
        top += 0.015
    z = big * math.cos(math.pi / 8) + 0.0012
    B.m.quad([(-0.036, 0.002, z), (0.036, 0.002, z), (0.036, 0.012, z), (-0.036, 0.012, z)],
             [B.A.point("plate_name", 0.02, 0.98), B.A.point("plate_name", 0.98, 0.98), B.A.point("plate_name", 0.98, 0.02), B.A.point("plate_name", 0.02, 0.02)])
    return top


def _v3(x, y, z):
    return np.array([x, y, z], dtype=float)


def base_motif(B, d, top):
    """Rare: small 3D ornaments on the base. Epic / Legendary: a motif rising around her."""
    r, m = d["rarity"], d.get("motif")
    if r in ("Common", "Uncommon"):
        return
    ring = [(0.072, 0.050), (-0.070, 0.040), (0.040, -0.062), (-0.050, -0.058)]
    if r == "Rare":
        for k, (x, z) in enumerate(ring[:3]):
            c = _v3(x, top + 0.008, z)
            if m == "bats":
                b0 = c + _v3(0, 0.020 + 0.012 * k, 0)
                B.ellipsoid(tuple(b0), (0.004, 0.006, 0.004), "dark", nu=8, nv=6)
                for side in (-1, 1):
                    tube(B, [b0, b0 + _v3(side * 0.010, 0.006, 0), b0 + _v3(side * 0.020, -0.002, 0)], [0.002, 0.005, 0.001], "dark",
                         nu=5, nv=6, depth=0.25, side=(0, 1, 0))
            elif m == "flames":
                for j in range(3):
                    tube(B, [c + _v3(0.006 * (j - 1), 0, 0), c + _v3(0.004 * (j - 1), 0.012, 0.002), c + _v3(0.002 * (j - 1), 0.022 + 0.006 * (j == 1), 0)],
                         [0.006, 0.004, 0.0006], "gemcore", nu=5, nv=6)
            elif m == "shells":
                shell(B, c, 0.020, 1.0, facing=(x, 1.2, z))
            else:   # roses / ribbons
                rose(B, c + _v3(0, 0.004, 0), 0.008, 1.0, region="gem", centre="gemcore", facing=(0, 1, 0.3))
        return
    if m == "moon":
        cy, cz = top + 0.236, -0.080
        crescent(B, (0.0, cy, cz), 0.050, 0.011, "base_trim", normal=(0, 0, 1), up=(0.55, 0.85, 0), open_deg=100, nu=7, nv=24)
        tube(B, [(0.0, top - 0.002, cz), (0.0, top + 0.10, cz), (0.0, cy - 0.047, cz)], [0.0040, 0.0035, 0.0030], "base_trim", nu=8)
        for (x, y, z, rr) in ((0.070, 0.050, 0.060, 0.012), (-0.080, 0.090, 0.040, 0.010), (0.090, 0.180, -0.020, 0.009)):
            star4(B, (x, top + y, z), rr, "gemcore")
    elif m == "sun":       # Aurelia: a sunburst rising behind her and floating feathers
        c = _v3(0.0, top + 0.236, -0.085)
        tube(B, [_v3(0, top - 0.002, -0.085), c - _v3(0, 0.04, 0)], [0.004, 0.0035], "base_trim", nu=8, nv=4)
        ring_pts = [c + 0.040 * _v3(math.cos(a), math.sin(a), 0) for a in np.linspace(0, TAU, 25)]
        tube(B, ring_pts, [0.0035] * 25, "base_trim", nu=5, nv=36, caps=False)
        for k in range(16):
            a = TAU * k / 16
            L = 0.020 if k % 2 == 0 else 0.012
            root = c + 0.040 * _v3(math.cos(a), math.sin(a), 0)
            tube(B, [root, root + _v3(math.cos(a), math.sin(a), 0) * L], [0.005, 0.0006], "base_trim", nu=4, nv=4)
        for (x, y, z) in ((0.08, 0.05, 0.05), (-0.085, 0.10, 0.03), (0.09, 0.20, -0.02)):
            tube(B, [_v3(x, top + y, z), _v3(x + 0.01, top + y + 0.02, z), _v3(x + 0.025, top + y + 0.03, z)], [0.002, 0.007, 0.0008],
                 "feather", nu=5, nv=6, depth=0.25, side=(0, 1, 0))
    elif m == "cosmos":    # Astrielle: tilted orbit rings with planets round her
        for k, (tilt, R_, y) in enumerate(((16, 0.110, 0.10), (-12, 0.098, 0.17))):
            Rm = MW.rot_xyz(rz=tilt, rx=8)
            pts = [_v3(0, top + y, -0.01) + Rm @ _v3(R_ * math.cos(a), 0, R_ * 0.55 * math.sin(a)) for a in np.linspace(0, TAU, 33)]
            tube(B, pts, [0.0025] * 33, "base_trim", nu=4, nv=48, caps=False)
            p = pts[(7 + 11 * k) % 32]
            B.ellipsoid(tuple(p), (0.011 - 0.003 * k,) * 3, "gem", nu=12, nv=8)
        for (x, y, z) in ((0.075, 0.04, 0.06), (-0.08, 0.15, 0.05), (0.06, 0.28, -0.03), (-0.05, 0.31, -0.02)):
            star4(B, (x, top + y, z), 0.010, "gemcore")
    elif m == "stars":     # Elarielle: an arch of stars over her and a crescent at her feet
        for k in range(15):
            a = math.pi * k / 14
            p = (0.135 * math.cos(a), top + 0.03 + 0.31 * math.sin(a) ** 0.85, -0.090)
            star4(B, p, 0.018 if k % 2 == 0 else 0.011, "gemcore", depth=0.5)
        pts = [_v3(0.135 * math.cos(a), top + 0.03 + 0.31 * math.sin(a) ** 0.85, -0.096) for a in np.linspace(0, math.pi, 29)]
        tube(B, pts, [0.003] * 29, "base_trim", nu=4, nv=48, caps=False)
        crescent(B, (0.0, top + 0.012, 0.070), 0.030, 0.008, "base_trim", normal=(0, 1, 0.2), up=(0, 0, 1), open_deg=110)
    elif m == "dream":     # Luminelle: soft clouds on the base and crystals rising
        for k in range(9):
            a = TAU * k / 9
            B.ellipsoid((0.085 * math.cos(a), top + 0.010, 0.085 * math.sin(a)), (0.030, 0.018, 0.026), "cloud", nu=12, nv=6)
        for (x, z, h) in ((0.085, 0.050, 0.07), (-0.080, 0.045, 0.06), (0.060, -0.075, 0.09), (-0.065, -0.070, 0.08)):
            faceted(B, _v3(x, top + h * 0.45, z), 0.018, h, "crystal", 1.0, nu=5)


# =========================================================================== assemble
DEFAULTS = dict(skin=(248, 226, 214), lips=(206, 120, 140), base=(40, 36, 60), outfit="gown", pose="staff_orb",
                hair_style="long", pattern="satin", props=[], motif=None)


def resolved(key):
    d = dict(DEFAULTS)
    d.update(BY_KEY[key])
    d.update(STYLE.get(key, {}))
    d.setdefault("hair2", _shade(d["hair"], 0.70))
    d.setdefault("base2", d["trim"])
    return d


def build(key):
    d = resolved(key)
    A = atlas(d)
    B = K.Builder(A)
    top = build_base(B, d)
    base_motif(B, d, top)
    fig = K.Builder(A)
    s = FIG_H
    build_figure(fig, d, s)
    if d["outfit"] == "gown_cape":
        prop_cape(fig, d, s)
    for p in d["props"]:
        if p not in PROPS:
            raise NotImplementedError("%s: unknown prop %s" % (key, p))
        PROPS[p](fig, d, s)
    B.m.merge(fig.m, translate=(0, top, 0))
    return B.m.check(item_id(key)), A


# =========================================================================== the blind box
def box_art(W=256, H=320):
    """Front of the Velvet Eclipse box: plum velvet, a gold crescent, the series name."""
    S = SS
    im = _vgrad(max(W, H) * S, (70, 30, 90), (24, 14, 40)).resize((W * S, H * S))
    d = ImageDraw.Draw(im)
    gold = (236, 196, 110, 255)
    d.rectangle([6 * S, 6 * S, (W - 6) * S, (H - 6) * S], outline=gold, width=3 * S)
    d.rectangle([12 * S, 12 * S, (W - 12) * S, (H - 12) * S], outline=(170, 130, 70, 255), width=S)
    # crescent: a gold disc with a dark disc cut out of it
    cx, cy, r = W / 2 * S, 120 * S, 56 * S
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=gold)
    d.ellipse([cx - r + 26 * S, cy - r - 10 * S, cx + r + 26 * S, cy + r - 10 * S], fill=(52, 24, 70, 255))
    rng = np.random.default_rng(11)
    for _ in range(26):
        x, y = rng.uniform(20, W - 20) * S, rng.uniform(20, 200) * S
        rr = rng.uniform(1.0, 2.6) * S
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(255, 236, 200, 255))
    f = K.font(30 * S)
    for i, line in enumerate(["VELVET", "ECLIPSE"]):
        tw = d.textlength(line, font=f)
        d.text(((W * S - tw) / 2, (196 + i * 34) * S), line, font=f, fill=gold)
    f2 = K.font(15 * S)
    t = "GLAMOUR & FANTASY STATUES"
    tw = d.textlength(t, font=f2)
    d.text(((W * S - tw) / 2, 272 * S), t, font=f2, fill=(230, 210, 240, 255))
    f3 = K.font(13 * S)
    t = "Jamie's Treasures  -  1 of 20"
    tw = d.textlength(t, font=f3)
    d.text(((W * S - tw) / 2, 294 * S), t, font=f3, fill=(200, 170, 120, 255))
    return im.resize((W, H), Image.LANCZOS)


def build_box():
    A = core.Atlas(512, background=(40, 20, 56, 255))
    A.add("front", box_art())
    A.add("side", _vgrad(64, (70, 30, 90), (30, 16, 46)))
    A.add("top", metal((236, 196, 110)))
    A.finish()
    m = core.Mesh()
    w, h, d = 0.08, 0.10, 0.06
    m.box(-w / 2, w / 2, 0, h, -d / 2, d / 2, A.uv("side"), top=A.uv("top"), front=A.uv("front"), back=A.uv("front"))
    return m.check("velvet_box"), A
