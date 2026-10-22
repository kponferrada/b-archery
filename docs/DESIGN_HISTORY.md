> Written while the crossbows were part of Jamie's Treasures (0.11.0-0.11.6). Since Jamie's Crossbows 0.1.0 the names are JC_* / JamiesCrossbows (module, Lua, sounds, shader jc_glow, ammo type jamiescrossbows:crossbow_bolt) and the mod stands alone.

# Treasured Crossbows (0.11.0 - 0.11.3) - audit, design and test status

Jamie's brief: 10 original, functional, individually glowing crossbows, added to Jamie's
Treasures without touching the Treasured Blades. **Status (0.11.3): all ten built.** The
Silent Reaper prototype was seen in game by Jamie (in hand, glow, firing, bolt on the floor);
the other nine are checked offline (renders, scripts) and not yet seen in game.

## 1. What Build 42.21 offers (read from the installed game, not assumed)

| Need | What 42.21 has | Source | Used how |
|---|---|---|---|
| A crossbow item | **No vanilla crossbow or bolt** in 42.21 (no item, model, sound or animation names "crossbow"/"bow") | `media/scripts/**`, `projectzomboid.jar` | Built from the firearm system |
| Aiming, firing, hits | Aimed firearms (`Ranged = true`, `IsAimedFirearm = true`, `SwingAnim = Rifle`): the game's own aim, hit test, damage and hit chance, run by the server in MP | `items/weapon.txt` (Hunting Rifle) | Each crossbow is an aimed firearm |
| Projectiles | **None**: a firearm shot is a hit test; there is no flying projectile object to follow, pick up or render | jar, `weapon.txt` (`Projectilecount` = pellets per hit test) | No visible bolt in flight (limitation); recovery done another way (section 3) |
| Ammunition | `AmmoType` is a **registry** (`zombie.scripting.objects.AmmoType`): `AmmoType.register(id, itemKey)` is public; vanilla types are `base:bullets_308` etc. Mods register in `media/registries.lua` (the Legendary Katana mod registers its item tags there) | `AmmoType.class` (javap) | `jamiestreasures:crossbow_bolt` -> `JamiesTreasures.JT_CrossbowBolt` |
| Ammo use, reloading | The game's own: `MaxAmmo`, `HaveChamber`, `WeaponReloadType`, `InsertAllBulletsReload`, `RackAfterShoot` | `weapon.txt` (Hunting Rifle, Double-barrel, Revolver) | One bolt, no chamber, `boltactionnomag` reload (the rifle's two-handed reload animation) |
| Animations | Only the firearm sets (`Rifle`, `Handgun`, `Shotgun` swing anims; reload types). No crossbow-specific animation | `animsets`, `weapon.txt` | Rifle hold/aim/fire; rifle-style reload (limitation: it looks like loading a rifle) |
| Sounds | FMOD events for vanilla guns; mods add `sound X { clip { file = media/sound/....wav } }` (Authentic Z does) | `scripts/generated/sounds`, Workshop mods | Own WAVs made by maths (dev/art/sounds.py): shoot, load, cock, dry fire |
| Body impact | `physicsHitReaction <ammo type>` | `physics_hit_reactions.txt` | `physicsHitReaction crossbow_bolt` (softer than .308) |
| Glow | Model scripts take `shader = name`; the Treasured Blades ship `jt_glow` (texels with u >= 0.75 drawn unlit). Same model in the hands, while aiming/firing, attached on the back and on the floor | `ModelScript`, `media/shaders/jt_glow*` (0.5.0) | Same shader, same atlas layout, unchanged |
| Real light | Light needs an `IsoLightSource` per weapon, updated whenever it moves: a cost per crossbow, per move, for everyone nearby | jar | **Not used.** The glow is surface glow (it shines, it does not light the room). Honest limitation |
| MP | Firing, hit, damage and ammo are the server's firearm code; items are normal inventory items | jar / 42.21 MP | No custom network code for firing |

## 2. Balance (on their own, not the Katana parity)

From the game's Hunting Rifle, changed for a crossbow:

| | Hunting Rifle | Treasured Crossbow |
|---|---|---|
| Damage | 1.2 - 2.0 | 1.4 - 2.2 (one heavy bolt) |
| Crit | 30% x4 | 35% x4 |
| Hit chance | 50 | 55 |
| Range | 40 | 25 |
| Rounds | 4 + chamber | 1 (no chamber) |
| Reload | 25 | R loads a bolt; reload animation x2 speed (0.11.3) |
| Zombie hearing radius | 170 | **12** (almost silent) |
| Muzzle flash, casings, jams | yes | no |
| Durability | 10, 1 in 200 | 15, 1 in 150 |
| Weight | 4.0 | 3.2 |

No elemental damage or other bonus from the glow (cosmetic only). The blade buffs do not
apply to crossbows.

## 3. Bolts (0.11.1: you see them fly, you pick them up)

- `JT_CrossbowBolt`, ammunition (Ammo category). Admins give bundles of 10 (admin window).
- **Seeing it fly**: 42.21 draws a tracer for every firearm shot (`IsoBulletTracerEffects`), set
  per ammo type. **Tested in game (0.11.1): that class is not exposed to Lua**, so a mod cannot
  change it; the crossbow bolt flies as the game's default tracer streak. client/JT_CrossbowFx.lua
  now logs one plain line and stops (it would work if a later build exposes the class).
- **Picking it up**: the server makes the bolt once per shot (`OnWeaponSwingHitPoint`, the same
  event that takes the bolt out of the crossbow, and it runs on the dedicated server):
  a hit drops it at the target's feet; a miss drops it at the end of its flight, before the first
  wall, closed door or the crossbow's range (25). Clients send nothing (no duplication).
- **Breaking**: each shot breaks the bolt instead with 20% chance (sandbox
  `CrossbowBoltBreak`), lowered by the Crossbow skill (5% of it per level: 10% at level 10).
- **Crossbow skill** (`media/perks.txt`, under Firearms): +3 XP per hit, +2 per kill with a
  crossbow. Accuracy and crits stay on **Aiming**, the game's own firearm skill (the firearm code
  reads Aiming only).
- Not yet in loot or crafting: decided with the expansion.

## 3b. Quick reload (0.11.3)

- `shared/JT_CrossbowReload.lua`: on the Reload key going DOWN, with a crossbow in the main hand,
  not loaded, a bolt in the inventory and nothing queued, it calls the game's own
  `ISReloadWeaponAction.BeginAutomaticReload` (what a tap of R does for guns). The game's key-up
  handler then sees a busy queue and does nothing (no double reload). Holding R on a loaded
  crossbow still opens the firearm radial menu.
- Speed: `ISReloadWeaponAction.setReloadSpeed` sets the `ReloadSpeed` animation variable (client and
  server, from Reloading skill and panic); the hook multiplies it by 2 for crossbows only.
  `Reloadtime` in the script 40 -> 15.

## 3b2. The shot (0.11.5)

- Kick: the crossbows have `FireMode = Crossbow` (a free string in 42.21). The game's on-foot
  fire nodes need FireMode ""/Single/Auto/Burst, so `AnimSets/player/ranged/firearm/JT_CrossbowFire.xml`
  and `JT_CrossbowFireEmpty.xml` (FireMode = Crossbow) take over: the same events as FirearmSingle
  (AttackCollisionCheck, ShotDone, AttackAnim) on the aim clips (Bob_IdleAimRifle*), speed x2 for
  their double length. Vehicles keep the rifle node (it has no FireMode condition).
- Flash: CombatManager calls EffectsManager.startMuzzleFlash for every aimed firearm: an
  IsoLightSource (radius 18, colour 0.8/0.8/0.6 x night, life 6) on the shooter's square. No flash
  model (no MuzzleFlashModelKey). client/JT_CrossbowFx.lua removes that light with
  IsoCell:removeLamppost at OnWeaponSwingHitPoint and for 3 ticks after.
- Tracer: CombatManager.fireWeapon always adds it; IsoBulletTracerEffects is not exposed: unchanged.

## 3b3. Real bolts (0.11.6)

- Server (server/JT_Crossbows.lua): at OnWeaponSwingHitPoint (a bolt left the crossbow) it builds
  the line (facing + spread by Aiming), walks it in 0.25-tile steps: first zombie within 0.45 tiles
  (squares around the line, getMovingObjects), else the last open square before a wall / closed
  door, else 25 tiles. Broadcasts "boltFly" once, applies the result after dist / 24 s:
  damage = Min..MaxDamage, crit (CriticalChance + 2 x Aiming) x CritDmgMultiplier; health <= 0 ->
  zombie:Kill(weapon, shooter), else setHealth + stagger. Then the old land/break code.
- Shared (JT_CrossbowReload.lua): MaxRange 0.7 from OnWeaponSwing to OnPlayerAttackFinished, so the
  game's own hit test finds nothing and its tracer is ~0.7 tiles.
- Client (JT_CrossbowFx.lua): a local-only world item JT_CrossbowBoltFlying (AddWorldInventoryItem
  with transmit false) moved with setOffset / re-added when it changes square; yaw from the line
  (Fx.YAW_OFFSET if the model points the wrong way); removed on arrival; blood splat on a hit.
- **Untested in game:** the model's facing, how smooth it looks, and in MP whether other players see
  a non-lethal hit's stagger (the server sets it; a kill is the game's own and is synced).

## 3b4. Animations (0.1.1, read from the 42.21 install)

- Shot: JC_CrossbowFire.xml now uses the vanilla FirearmDefault clip set (`Bob_AttackRifle_Small`,
  `Up45/Up75/Down45/Down75_Small`, idle aim at recoilVarY 1) at singleShootSpeed x2. The old node played
  `Bob_IdleAimRifle*` at x5: no motion at all, the shot looked like a glitch.
- Reload: `boltactionnomag` = LoadRifleNoMag (`Bob_Reload_Shotgun_Load`, 0.70 s); no rack (HaveChamber false,
  NeedToBeClosedOnceReload unset). AnimState sorts nodes by m_ConditionPriority, then condition count, and takes
  the first match, so `actions/JC_CrossbowLoad.xml` (priority 10, + `JCCrossbow = true`) replaces it with
  `Bob_Reload_Lever_Rack` (1.133 s). JC_Reload.lua sets `JCCrossbow` and `JCReloadSpeed = ReloadSpeed x 1.92` in
  the setReloadSpeed hook; the MP server ends a bolt-action load after 0.59 s / ReloadSpeed (serverStart), and
  1.133 / 1.92 = 0.59, so client clip and server timer end together.
  Limitation: other players in MP may still see the rifle clip (JCCrossbow is set on the reloading client).
- Flying bolt: IsoWorldInventoryObject.setOffset = set fields + sync(1) + invalidateRenderChunkLevel(256).
  The look-only bolt now uses setOffX/Y/Z + invalidateRenderChunkLevel(256) (no sync).
  Untested in game: the facing sign (`Fx.YAW_SIGN`).

## 3c. The ten designs (dev/art/crossbows.py)

| Crossbow | Limbs | Stock | Sight | Detail |
|---|---|---|---|---|
| Silent Reaper | recurve | skeleton | red dot | crimson rail lines |
| Frostbite | forward | thumbhole | crystal | frost crystals at the limbs |
| Verdant Stalker | straight | wood | peep | carved leaves with glowing veins |
| Stormbreaker | compound (cams) | heavy | scope | lightning zigzags |
| Golden Viper | recurve | ornate | serpent | gold serpent along the rail |
| Emberfall | deflex | wood | peep | ember cracks in the stock |
| Moonshadow | forward | thumbhole | crescent | crescents on the limb tips |
| Ironwood Sentinel | straight | heavy | peep | steel straps and rivets |
| Jade Phantom | deflex | skeleton | red dot | glowing jade panels |
| Obsidian Crown | compound (cams) | ornate | crown | crowns on rail and butt |

Same stats for all ten. Journal page "Treasured Crossbows" (10 items), admin-only, never in loot.

## 4. Files (prototype)

Added: `dev/art/crossbows.py`, `dev/art/sounds.py`, `lua/server/JamiesTreasures/JT_Crossbows.lua`,
`media/registries.lua`, `scripts/JamiesTreasures_Crossbows.txt`, `scripts/JamiesTreasures_Sounds.txt`,
`sound/JamiesTreasures/*.wav`, the crossbow and bolt meshes, textures, icons, sticker and Inspect frames.
Changed: `dev/catalog.py` (CROSSBOW, CROSSBOWS_ENABLED, BOLT), `dev/build.py` (build_crossbow, build_bolt),
generated catalog / items / models / texts, `JT_Server.lua` (give: bolt bundle, crossbow stamp kind),
`JT_Client.lua` (info text), `JT_AdminWindow.lua` (one give-list line for bolts), tests.
Not changed: every Treasured Blade file, value and model (checked by `check_scripts.py`).

## 5. Test status

| Test | Status |
|---|---|
| Offline: scripts, ammo type, sounds, glow texture, blades untouched (check_scripts.py) | pass |
| Offline: bolt recovery, admin give, not in loot, not in journal (run_tests.lua) | pass |
| In game: item and icon show | **untested** |
| In game: model in hand, grip alignment, aiming pose | **untested** |
| In game: glow in hand / aiming / firing / on the floor | **untested** |
| In game: loads the bolt (registries.lua ammo type) | **untested** (the main risk) |
| In game: fires, hits, damage, bolt used, reload, dry fire | **untested** |
| In game: sounds | **untested** |
| In game: the bolt streak flies visibly (speed, colour) | **untested** |
| In game: the bolt lies where it landed (hit / miss / wall), ~1 in 5 breaks | **untested** |
| In game: Crossbow skill in the skills list, XP on hits and kills | **untested** |
| MP: dedicated server + 2 clients | **untested** |
| Blades still the same in game | **untested** (offline: unchanged) |

## 6. Prototype test plan (Silent Reaper)

1. Load the WIP in a solo test world. Console: no errors mentioning `registries.lua`, `AmmoType`,
   `JT_Crossbow`, `crossbow_bolt`.
2. Admin window: give **Silent Reaper Crossbow** and **Crossbow Bolt (bundle of 10)**.
3. Equip it (both hands): it sits in the hands like a rifle; red lines glow; aim (right-click):
   the glow stays; check it from several sides, day and night.
4. Reload (R): one bolt goes in; the counter shows 1/1. Fire at a zombie: the thump sound, the bolt
   count goes to 0, the zombie is hit. Fire again empty: dry click.
5. Shoot at zombies and at an empty street: watch the bolt fly; walk over and pick it up where it
   landed (at the zombie's feet, or before the wall it hit). About 1 shot in 5 breaks it.
   The skills screen shows **Crossbow** under Firearms, gaining XP with hits and kills.
6. Drop it: it lies on the floor and glows. Put it on your back: it shows there.
7. Swing a Treasured Blade: still the same (buff, glow, stats).
8. MP (dedicated server + 2 clients): steps 2-6 on both clients; each sees the other's crossbow and shots.
