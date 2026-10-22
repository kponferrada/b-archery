"""Jamie's Crossbows - what the mod contains (the data dev/build.py turns into the mod).

Ten crossbows (dev/art/crossbows.py DESIGNS), one bolt, one skill. Split out of Jamie's
Treasures 0.11.6 into its own mod (Jamie, 2026-10-14); the history before that is in the
Jamie's Treasures repo (docs/CROSSBOWS.md there, tags v0.11.0-v0.11.6).
"""
MOD_ID = "JamiesCrossbowsWIP"
MODULE = "JamiesCrossbows"          # item script module, Lua namespace and network channel
AMMO_TYPE = "jamiescrossbows:crossbow_bolt"

# The weapon script, from the game's Hunting Rifle (42.21 items/weapon.txt, the aimed
# two-handed long gun the crossbow is held, aimed and reloaded like), changed for a
# crossbow: one bolt, no chamber, quick to reload, almost silent (SoundRadius 12 vs the
# rifle's 170), no muzzle flash model, no cartridge sounds, never jams, its own fire mode
# (FireMode = Crossbow: our animation nodes, no recoil). With real bolts on (sandbox), the
# game's hit test is not used at all: the server flies the bolt (lua/server/JC_Server.lua).
CROSSBOW = [
    ("DisplayCategory", "Weapon"), ("ItemType", "base:weapon"), ("Weight", "3.2"),
    ("AimingPerkCritModifier", "6"), ("AimingPerkHitChanceModifier", "4"), ("AimingPerkMinAngleModifier", "0.01"),
    ("AimingPerkRangeModifier", "0"), ("Aimingtime", "55"),
    ("AmmoType", AMMO_TYPE), ("AttachmentType", "Rifle"),
    ("AimReleaseSound", "MSR788AimRelease"), ("BringToBearSound", "MSR788BringToBear"), ("BreakSound", "MSR788Break"),
    ("ClickSound", "JC_CrossbowDryFire"), ("ConditionLowerChanceOneIn", "150"), ("ConditionMax", "15"),
    ("CritDmgMultiplier", "4.0"), ("CriticalChance", "35.0"), ("DoorDamage", "3"), ("DropSound", "MSR788Drop"),
    ("EjectAmmoSound", "JC_CrossbowLoad"), ("EjectAmmoStartSound", "MSR788EjectAmmoStart"), ("EjectAmmoStopSound", "MSR788EjectAmmoStop"),
    ("EquipSound", "MSR788Equip"), ("FireMode", "Crossbow"), ("HaveChamber", "false"), ("HitChance", "55"), ("HitSound", "BulletImpact"),
    ("IdleAnim", "Idle_Weapon2"), ("ImpactSound", "null"), ("InsertAllBulletsReload", "true"),
    ("InsertAmmoSound", "JC_CrossbowLoad"), ("InsertAmmoStartSound", "JC_CrossbowCock"), ("InsertAmmoStopSound", "JC_CrossbowCock"),
    ("IsAimedFirearm", "true"), ("JamGunChance", "0"), ("KnockBackOnNoDeath", "true"), ("KnockdownMod", "2.0"),
    ("MaxAmmo", "1"), ("MaxDamage", "2.2"), ("MaxHitcount", "1"), ("MaxRange", "25.0"), ("MinSightRange", "2"), ("MaxSightRange", "10.0"),
    ("MinAngle", "0.95"), ("MinDamage", "1.4"), ("MinRange", "0.61"), ("MinimumSwingtime", "0.5"),
    ("MultipleHitConditionAffected", "false"), ("NPCSoundBoost", "1.0"), ("PiercingBullets", "false"), ("Projectilecount", "1"),
    ("PushBackMod", "0.3"), ("RackAfterShoot", "false"), ("RackSound", "JC_CrossbowCock"), ("Ranged", "true"), ("RecoilDelay", "15"),
    ("Reloadtime", "15"), ("RequiresEquippedBothHands", "true"), ("RunAnim", "Run_Weapon2"),
    ("SoundGain", "1.0"), ("SoundRadius", "12"), ("SoundVolume", "30"), ("SplatBloodOnNoDeath", "true"), ("SplatNumber", "2"),
    ("SplatSize", "2"), ("StopPower", "15.0"), ("SubCategory", "Firearm"), ("SwingAmountBeforeImpact", "0.0"), ("SwingAnim", "Rifle"),
    ("SwingSound", "JC_CrossbowShoot"), ("Swingtime", "0.5"), ("ToHitModifier", "1.5"), ("TwoHandWeapon", "true"),
    ("UnequipSound", "MSR788UnEquip"), ("UseEndurance", "false"), ("WeaponReloadType", "boltactionnomag"),
    ("Tags", "base:firearm"),
]
# the Hunting Rifle's model attachments (models_weapons.txt, model HuntingRifle): our meshes
# are built in its frame; the muzzle moved to where a bolt leaves the rail
CROSSBOW_ATTACHMENTS = [
    ("muzzle", "0.0 0.44 0.045", "-90.0 0.0 180.0"),
    ("world", "0.012 0.15 0.0", "180.0 0.0 180.0"),
]
BOLT = dict(id="JC_CrossbowBolt", name="Crossbow Bolt", weight=0.05)
BOLT_FLYING = "JC_CrossbowBoltFlying"
BOLT_BREAK = 0.2           # sandbox BoltBreak default (percent / 100)
BOLT_BUNDLE = 10           # admin give: bolts per bundle
CROSSBOW_PERK = dict(name="Crossbow", parent="Firearm", xp=(75, 150, 300, 750, 1500, 3000, 4500, 6000, 7500, 9000))


def crossbows():
    from art.crossbows import DESIGNS, item_id
    return [dict(id=item_id(d["key"]), key=d["key"], name=d["name"] + " Crossbow", lore=d["lore"]) for d in DESIGNS]
