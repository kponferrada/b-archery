#!/usr/bin/env python3
"""Jamie's Crossbows - checks the mod's scripts against each other (and the game, with --game).

    python3 check_scripts.py <media folder> [--game <game media folder>]
"""
import json
import pathlib
import re
import sys
import xml.dom.minidom

media = pathlib.Path(sys.argv[1])
game = pathlib.Path(sys.argv[sys.argv.index("--game") + 1]) if "--game" in sys.argv else None
checks, problems = 0, []


def check(cond, msg):
    global checks
    checks += 1
    if not cond:
        problems.append(msg)
        print("PROBLEM:", msg)


def read(p):
    return p.read_text(encoding="utf-8") if p.exists() else ""


def props(body):
    return dict(re.findall(r"^\s*(\w+)\s*=\s*([^,\n]*),", body, re.M))


scripts = media / "scripts"
items_txt = read(scripts / "JamiesCrossbows_Items.txt")
models_txt = read(scripts / "JamiesCrossbows_Models.txt")
item_bodies = {m.group(1): m.group(2) for m in re.finditer(r"item (\w+)\s*\{(.*?)\n    \}", items_txt, re.S)}
model_bodies = {m.group(1): m.group(2) for m in re.finditer(r"model (\w+)\s*\{(.*?)\n    \}", models_txt, re.S)}
cat = read(media / "lua" / "shared" / "JamiesCrossbows" / "JC_Catalog.lua")
xbows = re.findall(r'\{id = "(\w+)", key = "(\w+)"', cat)
bolt = re.search(r'bolt = "(\w+)"', cat).group(1)
flying = re.search(r'boltFlying = "(\w+)"', cat).group(1)
tr = media / "lua" / "shared" / "Translate" / "EN"
texts = {}
for f in tr.glob("*.json"):
    texts.update(json.loads(f.read_text(encoding="utf-8")))

check(len(xbows) == 10, "ten crossbows in the catalog (%d)" % len(xbows))
reg = read(media / "registries.lua")
m_reg = re.search(r'AmmoType\.register\("([\w:]+)", "([\w.]+)"\)', reg)
check(m_reg is not None, "registries.lua registers the ammo type")
check(m_reg and m_reg.group(2) == "JamiesCrossbows." + bolt, "the ammo type's item is the bolt")
phys = read(scripts / "JamiesCrossbows_Physics.txt")
our_sounds = set(re.findall(r"^\s*sound (\w+)", read(scripts / "JamiesCrossbows_Sounds.txt"), re.M))
for s in our_sounds:
    check((media / "sound" / "JamiesCrossbows" / (s + ".wav")).exists(), "sound file " + s)
vanilla_sounds = set()
if game:
    for sf in (game / "scripts").rglob("*.txt"):
        vanilla_sounds.update(re.findall(r"^\s*sound (\w+)", sf.read_text(encoding="utf-8", errors="ignore"), re.M))

for xid, key in xbows:
    body = item_bodies.get(xid, "")
    check(bool(body), "item script " + xid)
    xp = props(body)
    check(xp.get("AmmoType") == (m_reg.group(1) if m_reg else None), xid + ": AmmoType = the registered type")
    check(xp.get("WeaponSprite") == "JamiesCrossbows." + xid, xid + ": WeaponSprite names its model")
    check(xp.get("MaxAmmo") == "1" and xp.get("Ranged") == "true" and xp.get("IsAimedFirearm") == "true", xid + ": one-bolt aimed weapon")
    check(xp.get("FireMode") == "Crossbow", xid + ": FireMode = Crossbow (our animation nodes)")
    check("MuzzleFlashModelKey" not in xp and "ShellFallSound" not in xp, xid + ": no muzzle flash model, no cartridge")
    check(xp.get("Icon") == xid and (media / "textures" / ("Item_" + xid + ".png")).exists(), xid + ": icon")
    check(("Tooltip_JC_Crossbow_" + key) in texts and ("JamiesCrossbows." + xid) in texts, xid + ": name and tooltip text")
    for k, v in xp.items():
        if k.endswith("Sound") and v != "null":
            check(v in our_sounds or not game or v in vanilla_sounds, "%s: sound %s = %s exists" % (xid, k, v))
    md = model_bodies.get(xid, "")
    check("shader = jc_glow" in md, xid + ": model uses jc_glow")
    check("attachment world" in md and "attachment muzzle" in md, xid + ": world and muzzle attachments")
    mesh = re.search(r"mesh = ([\w/]+)", md)
    check(mesh and (media / "models_X" / (mesh.group(1) + ".x")).exists(), xid + ": mesh file")
    tx = re.search(r"texture = ([\w/]+)", md)
    check(tx and (media / "textures" / (tx.group(1) + ".png")).exists(), xid + ": texture file")
    if tx and (media / "textures" / (tx.group(1) + ".png")).exists():
        from PIL import Image
        im = Image.open(media / "textures" / (tx.group(1) + ".png")).convert("RGB")
        w, h = im.size
        right = im.crop((int(w * 0.77), 0, w, h)).getcolors(1 << 20) or []
        check(any(sum(c) > 300 for _, c in right), xid + ": glow column has glow colours")
    if m_reg:
        check(("physicsHitReaction " + m_reg.group(1).split(":")[-1]) in phys, xid + ": physics hit reaction")

for iid in (bolt, flying):
    b = props(item_bodies.get(iid, ""))
    check(bool(b), "item script " + iid)
    gm = b.get("WorldStaticModel", "")
    check(gm in model_bodies and "shader = jc_glow" in model_bodies[gm], iid + ": glowing floor model " + gm)
    check(("JamiesCrossbows." + iid) in texts, iid + ": name text")
check("Tooltip_JC_CrossbowBolt" in texts, "bolt tooltip")

for f in ("jc_glow.vert", "jc_glow.frag", "jc_glow_instanced.vert", "jc_glow_instanced.frag", "jc_glow_static.vert",
          "jc_glow_static_instanced.vert"):
    check((media / "shaders" / f).exists(), "shader " + f)

pk = read(media / "perks.txt")
for perk in re.findall(r"^perk (\w+)", pk, re.M):
    check("IGUI_perks_" + perk in texts and "IGUI_perks_%s_Description" % perk in texts, "skill texts " + perk)
check("perk Crossbow" in pk, "the Crossbow skill")

sb = read(media / "sandbox-options.txt")
for opt in re.findall(r"^option JamiesCrossbows\.(\w+)", sb, re.M):
    check("Sandbox_JamiesCrossbows_" + opt in texts and "Sandbox_JamiesCrossbows_%s_tooltip" % opt in texts, "sandbox text " + opt)
check("Sandbox_JamiesCrossbows" in texts, "sandbox page name")
lua = "\n".join(p.read_text(encoding="utf-8") for p in (media / "lua").rglob("*.lua") if "Translate" not in p.parts)
for opt in re.findall(r'opt(?:Num|Bool)\("(\w+)"', lua):
    check(("option JamiesCrossbows." + opt) in sb, "Lua reads sandbox option %s, which exists" % opt)
for key in set(re.findall(r'"(IGUI_JC_\w+)"', lua)):
    check(key in texts, "text " + key)
check("ContextMenu_FireMode_Crossbow" in texts, "fire mode name text")

anim = media / "AnimSets" / "player" / "ranged" / "firearm"
for fn, empty in (("JC_CrossbowFire.xml", "false"), ("JC_CrossbowFireEmpty.xml", "true")):
    f = anim / fn
    check(f.exists(), "animation node " + fn)
    if not f.exists():
        continue
    dom = xml.dom.minidom.parse(str(f))
    conds = {}
    for c in dom.getElementsByTagName("m_Conditions"):
        v = c.getElementsByTagName("m_Value")[0].firstChild
        conds[c.getElementsByTagName("m_Name")[0].firstChild.data] = v.data if v else ""
    check(conds.get("FireMode") == "Crossbow" and conds.get("RangedWeaponEmpty") == empty, fn + ": conditions")
    evs = [e.getElementsByTagName("m_EventName")[0].firstChild.data for e in dom.getElementsByTagName("m_Events")]
    need = ["AttackCollisionCheck", "AttackAnim"] if empty == "false" else ["WeaponEmptyCheck", "playClickSound"]
    check(all(n in evs for n in need), fn + ": the game's shot events")
    clips = {a.firstChild.data for a in dom.getElementsByTagName("m_AnimName")}
    check(not any("Attack" in c and not c.endswith("_Small") for c in clips), fn + ": only the small (soft) recoil clips")
    if game:
        for c in clips:
            check((game / "anims_X" / "Bob" / (c + ".x")).exists(), fn + ": clip " + c)

f = media / "AnimSets" / "player" / "actions" / "JC_CrossbowLoad.xml"
check(f.exists(), "animation node JC_CrossbowLoad.xml")
if f.exists():
    dom = xml.dom.minidom.parse(str(f))
    conds = {c.getElementsByTagName("m_Name")[0].firstChild.data: c.getElementsByTagName("m_Value")[0].firstChild.data
             for c in dom.getElementsByTagName("m_Conditions")}
    check(conds == {"PerformingAction": "Reload", "WeaponReloadType": "boltactionnomag", "isLoading": "true",
                    "JCCrossbow": "true"}, "JC_CrossbowLoad.xml: conditions (the rifle's + JCCrossbow)")
    pr = dom.getElementsByTagName("m_ConditionPriority")
    check(pr and int(pr[0].firstChild.data) > 0, "JC_CrossbowLoad.xml: wins over the rifle's LoadRifleNoMag")
    evs = [e.getElementsByTagName("m_EventName")[0].firstChild.data for e in dom.getElementsByTagName("m_Events")]
    check("loadFinished" in evs, "JC_CrossbowLoad.xml: loadFinished (the bolt goes in)")
    check(dom.getElementsByTagName("m_SpeedScale")[0].firstChild.data == "JCReloadSpeed", "JC_CrossbowLoad.xml: timed by JCReloadSpeed")
    check('"JCReloadSpeed"' in lua and '"JCCrossbow"' in lua, "Lua sets JCCrossbow and JCReloadSpeed")
    if game:
        c = dom.getElementsByTagName("m_AnimName")[0].firstChild.data
        check((game / "anims_X" / "Bob" / (c + ".x")).exists(), "JC_CrossbowLoad.xml: clip " + c)

print("%d checks, %d problems" % (checks, len(problems)))
sys.exit(1 if problems else 0)
