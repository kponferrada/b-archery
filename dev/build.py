#!/usr/bin/env python3
"""Jamie's Crossbows - builds every GENERATED file of the mod from dev/catalog.py and
dev/art (meshes, textures, icons, sounds, item / model / sound / physics scripts, the
Crossbow skill, the ammo type, translations, the Lua catalog, poster and icon).

Hand-made files are NOT touched: lua/ (except JC_Catalog.lua), shaders/, AnimSets/,
sandbox-options.txt, mod.info.

    python3 dev/build.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "art"))

import catalog as C  # noqa: E402
from art import xwriter  # noqa: E402
import crossbows as XB  # noqa: E402
import sounds as SND  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

MOD_ID = os.environ.get("JC_MOD_ID", C.MOD_ID)
MODULE = C.MODULE
ROOT = os.path.dirname(HERE)
MOD = os.path.join(ROOT, "Contents", "mods", MOD_ID)
MEDIA = os.path.join(MOD, "42", "media")


def out(*p):
    path = os.path.join(MEDIA, *p)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def write_text(path, text):
    with open(path, "w", newline="\n", encoding="utf-8") as f:
        f.write(text)


def lua_str(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def mod_version():
    with open(os.path.join(MOD, "42", "mod.info"), encoding="utf-8") as f:
        for line in f:
            if line.startswith("modversion="):
                return line.split("=", 1)[1].strip()
    return "0"


def build_crossbow(it, items, models, names, tooltips, report):
    iid, key = it["id"], it["key"]
    m, A = XB.build(key)
    xwriter.write(m, out("models_X", "weapons", MODULE, iid + ".x"), iid, iid + ".png")
    A.img.convert("RGB").save(out("textures", "weapons", MODULE, iid + ".png"), optimize=True)
    XB.icon(m, A).save(out("textures", "Item_" + iid + ".png"))
    lo, hi = m.bounds()
    report.append("%-30s %5d tris  %.3f x %.3f x %.3f m" % (iid, len(m.tri), hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]))
    props = "\n".join("        %s = %s," % (k, v) for k, v in C.CROSSBOW)
    items.append("""    item %s
    {
        DisplayName = %s,
%s
        AmmoBox = %s.%s,
        Icon = %s,
        WeaponSprite = %s.%s,
        Tooltip = Tooltip_JC_Crossbow_%s,
    }
""" % (iid, it["name"], props, MODULE, C.BOLT["id"], iid, MODULE, iid, key))
    att = "".join("""        attachment %s
        {
            offset = %s,
            rotate = %s,
        }
""" % a for a in C.CROSSBOW_ATTACHMENTS)
    models.append("""    model %s
    {
        mesh = weapons/%s/%s,
        texture = weapons/%s/%s,
        shader = jc_glow,
%s    }
""" % (iid, MODULE, iid, MODULE, iid, att))
    names[MODULE + "." + iid] = it["name"]
    tooltips["Tooltip_JC_Crossbow_" + key] = it["lore"] + " Fires real bolts you see fly and can pick up again, almost silently."
    return XB.sticker(m, A, size=256)


def build_bolt(items, models, names, tooltips, report):
    b = C.BOLT
    m, A = XB.build_bolt()
    xwriter.write(XB.build_bolt_ground(m), out("models_X", b["id"] + ".x"), b["id"], b["id"] + ".png")
    A.img.convert("RGB").save(out("textures", "WorldItems", MODULE, b["id"] + ".png"), optimize=True)
    XB.bolt_icon(m, A).save(out("textures", "Item_" + b["id"] + ".png"))
    items.append("""    item %s
    {
        DisplayName = %s,
        DisplayCategory = Ammo,
        ItemType = base:normal,
        Weight = %s,
        Icon = %s,
        WorldStaticModel = %s_Ground,
        Tooltip = Tooltip_JC_CrossbowBolt,
        Tags = base:ammo,
    }
""" % (b["id"], b["name"], b["weight"], b["id"], b["id"]))
    # the bolt you see fly: a look-only copy, made on each client for the flight and removed
    # when it lands (never sent to the server, never in loot)
    items.append("""    item %s
    {
        DisplayName = Crossbow Bolt (in flight),
        DisplayCategory = Ammo,
        ItemType = base:normal,
        Weight = 0.0,
        Icon = %s,
        WorldStaticModel = %s_Ground,
    }
""" % (C.BOLT_FLYING, b["id"], b["id"]))
    names[MODULE + "." + C.BOLT_FLYING] = "Crossbow Bolt (in flight)"
    # drawn 1.8x and glowing (jc_glow), so a bolt on the floor can be found, also at night
    models.append("""    model %s_Ground
    {
        mesh = %s,
        texture = WorldItems/%s/%s,
        shader = jc_glow,
        scale = 1.8,
    }
""" % (b["id"], b["id"], MODULE, b["id"]))
    names[MODULE + "." + b["id"]] = b["name"]
    tooltips["Tooltip_JC_CrossbowBolt"] = ("Ammunition for Jamie's Crossbows. After a shot, pick it up where it landed; "
                                           "about 1 shot in 5 breaks it.")
    report.append("%-30s %5d tris  (bolt)" % (b["id"], len(m.tri)))


def physics():
    # how a bolt pushes a body (42.21 physics_hit_reactions.txt is keyed by ammo type; the .308's, softer)
    parts = ["pelvis", "spine", "head", "left_upper_leg", "left_lower_leg", "right_upper_leg", "right_lower_leg",
             "left_upper_arm", "left_lower_arm", "right_upper_arm", "right_lower_arm"]
    lines = ["        impulse_%s = %s," % (p, "25.0" if p in ("pelvis", "spine") else "15.0") for p in parts]
    lines += ["        upwardImpulse_%s = %s," % (p, "10.0") for p in parts]
    return ("/* Jamie's Crossbows - physics. GENERATED by dev/build.py. */\n"
            "module %s\n{\n    physicsHitReaction crossbow_bolt\n    {\n%s\n    }\n}\n" % (MODULE, "\n".join(lines)))


def poster(previews):
    W, H = 512, 512
    img = Image.new("RGBA", (W, H), (34, 30, 42, 255))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(30 + 20 * t), int(26 + 12 * t), int(40 + 26 * t), 255))
    cells = previews[:9]
    for i, p in enumerate(cells):
        x, y = (i % 3) * 170 + 1, (i // 3) * 170 + 1
        img.alpha_composite(p.resize((170, 170), Image.LANCZOS), (x, y))
    return img.convert("RGB")


def main():
    texts = json.load(open(os.path.join(HERE, "texts.json"), encoding="utf-8"))
    items, models, names, tooltips, report, previews = [], [], {}, {}, [], []
    xbows = C.crossbows()
    for it in xbows:
        previews.append(build_crossbow(it, items, models, names, tooltips, report))
    build_bolt(items, models, names, tooltips, report)

    write_text(out("scripts", "JamiesCrossbows_Items.txt"),
               "/* Jamie's Crossbows - items. GENERATED by dev/build.py. */\nmodule %s\n{\n    imports { Base }\n\n%s}\n"
               % (MODULE, "\n".join(items)))
    write_text(out("scripts", "JamiesCrossbows_Models.txt"),
               "/* Jamie's Crossbows - models. GENERATED by dev/build.py. */\nmodule %s\n{\n    imports { Base }\n\n%s}\n"
               % (MODULE, "\n".join(models)))
    write_text(out("scripts", "JamiesCrossbows_Physics.txt"), physics())
    write_text(out("scripts", "JamiesCrossbows_Sounds.txt"), SND.write_all(out("sound", MODULE)))
    pk = C.CROSSBOW_PERK
    write_text(os.path.join(MEDIA, "perks.txt"),
               "VERSION = 1,\n\n"
               "perk %s\n{\n    parent = %s,\n    translation = %s,\n    passive = false,\n%s\n}\n\n"
               "/* Jamie's Crossbows - the Crossbow skill. GENERATED by dev/build.py. */\n" % (
                   pk["name"], pk["parent"], pk["name"], "\n".join("    xp%d = %d," % (i + 1, v) for i, v in enumerate(pk["xp"]))))
    write_text(os.path.join(MEDIA, "registries.lua"),
               "-- Jamie's Crossbows - registries. GENERATED by dev/build.py.\n"
               "-- The crossbows' ammunition: AmmoType \"%s\" = the item %s.%s\n"
               "-- (42.21 AmmoType.register(id, itemKey); the game's own types are base:bullets_308 and so on).\n"
               "JamiesCrossbowsRegistries = JamiesCrossbowsRegistries or {}\n"
               "JamiesCrossbowsRegistries.CrossbowBolt = AmmoType.register(\"%s\", \"%s.%s\")\n"
               % (C.AMMO_TYPE, MODULE, C.BOLT["id"], C.AMMO_TYPE, MODULE, C.BOLT["id"]))

    # the Lua catalog
    L = ["-- Jamie's Crossbows - catalog. GENERATED by dev/build.py from dev/catalog.py; do not edit.",
         "JamiesCrossbows = JamiesCrossbows or {}",
         "JamiesCrossbows.Catalog = {",
         "    modVersion = %s," % lua_str(mod_version()),
         "    module = %s," % lua_str(MODULE),
         "    ammoType = %s," % lua_str(C.AMMO_TYPE),
         "    bolt = %s," % lua_str(C.BOLT["id"]),
         "    boltFlying = %s," % lua_str(C.BOLT_FLYING),
         "    boltBreak = %s," % C.BOLT_BREAK,
         "    boltBundle = %d," % C.BOLT_BUNDLE,
         "    crossbows = {"]
    for it in xbows:
        L.append("        {id = %s, key = %s, name = %s}," % (lua_str(it["id"]), lua_str(it["key"]), lua_str(it["name"])))
    L += ["    },", "}", "return JamiesCrossbows.Catalog", ""]
    write_text(out("lua", "shared", "JamiesCrossbows", "JC_Catalog.lua"), "\n".join(L))

    # translations (EN)
    tr = os.path.join("lua", "shared", "Translate", "EN")
    texts.setdefault("Tooltip.json", {}).update(tooltips)
    write_text(out(tr, "ItemName.json"), json.dumps(names, indent=2, ensure_ascii=False) + "\n")
    for fname, block in texts.items():
        write_text(out(tr, fname), json.dumps(block, indent=2, ensure_ascii=False) + "\n")

    # poster, icon, preview
    p = poster(previews)
    p.save(os.path.join(MOD, "poster.png"))
    p.save(os.path.join(MOD, "42", "poster.png"))
    ic = previews[0].resize((64, 64), Image.LANCZOS)
    bg = Image.new("RGBA", (64, 64), (34, 30, 42, 255))
    bg.alpha_composite(ic)
    bg.convert("RGB").save(os.path.join(MOD, "icon.png"))
    bg.convert("RGB").save(os.path.join(MOD, "42", "icon.png"))
    p.resize((256, 256), Image.LANCZOS).save(os.path.join(ROOT, "preview.png"))
    print("\n".join(report))
    print("built", MOD_ID, mod_version())


if __name__ == "__main__":
    main()
