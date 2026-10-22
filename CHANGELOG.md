# Changelog

## 0.1.1 WIP (2026-10-22) - animations
* The shot: tried the game's soft rifle-shot clips; in game the crossbow stopped shooting, so the shot node is back to the 0.1.0 version (aim pose). Debug lines log each shot while this is checked.
* **The reload** is a crossbow pull, not a rifle: new `AnimSets/player/actions/JC_CrossbowLoad.xml` (priority 10, only with a crossbow in the hands) plays a cocking pull (`Bob_Reload_Lever_Rack`) with the cock sound at the start and the bolt-drop sound near the end. Timed to end exactly when the game's load does (also on an MP server), so it is never cut short; if the animation never says the bolt is in, it is loaded anyway after 1.6x the expected time. Reload speed x1.25 (was x2, too fast to read): 0.59 s at Reloading 0.
* **The flying bolt**: in MP moved with setOffX/Y/Z instead of setOffset (setOffset also sent a network sync every tick for an object the server never had; solo keeps setOffset); a bolt that flies its whole range now falls in a curve instead of sliding down a ramp. `Fx.YAW_SIGN` / `Fx.YAW_OFFSET` in JC_Fx.lua if it points the wrong way.
* Tests: check_scripts.py checks the new reload node and the soft shot clips (with `--game`: that every clip exists in 42.21).

## 0.1.0 WIP (2026-10-14) - its own mod
* Jamie: the crossbows move out of Jamie's Treasures into their own mod, **Jamie's Crossbows**. It works on its own (Jamie's Treasures is not needed).
* Everything from Jamie's Treasures 0.11.0-0.11.6 (history in docs/DESIGN_HISTORY.md):
  * ten glowing crossbows: Silent Reaper, Frostbite, Verdant Stalker, Stormbreaker, Golden Viper, Emberfall, Moonshadow, Ironwood Sentinel, Jade Phantom, Obsidian Crown
  * **real bolts**: you see each bolt fly; it hits the first zombie in its path, stops at walls, and you pick it up where it lands (1 in 5 breaks)
  * press **R** to load (no wheel), quick reload, bolt counter on the hand slot
  * no gun kick, no gun flash, no bullet streak
  * the **Crossbow** skill (under Firearms)
* Admins: right-click the world > **Jamie's Crossbows (admin)** to give a crossbow or 10 bolts (sandbox "Who can give crossbows": admins, or admins and moderators).
* Sandbox page **Jamie's Crossbows**: Real bolts (on), Bolt breaks per shot (20%), Who can give crossbows.
* New names (a crossbow given in a Jamie's Treasures 0.11.x test world is not carried over).
* Fix: with real bolts on, shooting a zombie at point blank no longer gives the Crossbow XP twice (the game's own hit is ignored; the bolt gives the XP).
