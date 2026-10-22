-- Jamie's Crossbows - quick crossbow reload.
--
-- * R loads a bolt: pressing the game's Reload key with a crossbow in your hands
--   starts the game's own automatic reload (ISReloadWeaponAction.BeginAutomaticReload,
--   the same thing a quick tap of R does for guns) at once, on key DOWN. Nothing to open,
--   nothing to right-click. Holding R still opens the game's firearm radial menu when the
--   crossbow is already loaded or you have no bolts. Because the reload is queued on key
--   down, the game's own key-up handler sees a busy queue and does nothing (no double reload).
-- * Faster: the game times reloads by its "ReloadSpeed" variable (set from the Reloading
--   skill and panic in ISReloadWeaponAction.setReloadSpeed, on the client and the server).
--   With a crossbow in the hands it is multiplied by SPEED. Guns are unchanged.
-- * Its own animation: the same hook sets "JCCrossbow" (true with a crossbow in the hands)
--   and "JCReloadSpeed". AnimSets/player/actions/JC_CrossbowLoad.xml (priority 10, needs
--   JCCrossbow) then replaces the rifle's thumb-a-round-in clip with a cocking pull
--   (Bob_Reload_Lever_Rack, 1.13 s). JCReloadSpeed = ReloadSpeed x CLIP_FIT so the clip ends
--   exactly when the game's own load time does (the MP server times a bolt-action load at
--   0.59 s / ReloadSpeed; 1.133 / 0.59 = 1.92), so the pull is never cut short.
-- * real bolts (sandbox RealBolts): for the moment of a shot the crossbow's
--   range is cut to arm's length (Q.SHORT_RANGE), so the game's own gun hit test finds no
--   target and its bullet streak is only a few centimetres; the bolt itself is flown by
--   the server (server/JC_Server.lua). The range is put back when the attack ends, so
--   the tooltip and everything else see the normal 25. Same on the client and the server.
-- Runs only on a key press, a shot or when a reload starts; no per-frame work.

require "JamiesCrossbows/JC_Core"

local JC = JamiesCrossbows
JC.Reload = JC.Reload or {}
local Q = JC.Reload

Q.SPEED = 1.25      -- a load takes 0.59 s at Reloading 0, 0.26 s at 10 (was 2.0: 0.37 s, too fast to read)
Q.DEBUG = true      -- TEMPORARY: logs each crossbow reload to console.txt ([JamiesCrossbows] DEBUG ...)
Q.WATCHDOG = 1.6    -- safety net: load the bolt if the animation has not after 1.6x the expected time
Q.CLIP_FIT = 1.92   -- Bob_Reload_Lever_Rack length / the game's bolt-action load time

function Q.isCrossbow(item)
    return JC.isCrossbow(item)
end

-- ---------------------------------------------------------------------------- faster reload
function Q.wrapSpeed()
    if Q.wrapped or not ISReloadWeaponAction or not ISReloadWeaponAction.setReloadSpeed then
        return false
    end
    local orig = ISReloadWeaponAction.setReloadSpeed
    ISReloadWeaponAction.setReloadSpeed = function(character, rack)
        orig(character, rack)
        local ok = pcall(function()
            local cb = Q.isCrossbow(character:getPrimaryHandItem()) and true or false
            if cb then
                local speed = character:getVariableFloat("ReloadSpeed", 1.0) * Q.SPEED
                character:setVariable("ReloadSpeed", speed)
                character:setVariable("JCReloadSpeed", speed * Q.CLIP_FIT)
            end
            character:setVariable("JCCrossbow", cb)
            if cb and Q.DEBUG then
                JC.log("DEBUG reload start: rack=" .. tostring(rack) .. " ReloadSpeed=" .. tostring(character:getVariableFloat("ReloadSpeed", -1))
                    .. " JCReloadSpeed=" .. tostring(character:getVariableFloat("JCReloadSpeed", -1))
                    .. " JCCrossbow=" .. tostring(character:getVariableBoolean("JCCrossbow"))
                    .. " WeaponReloadType=" .. tostring(character:getVariableString("WeaponReloadType")))
            end
        end)
        if not ok and not Q.speedErr then
            Q.speedErr = true
            JC.log("Crossbow quick reload: could not change the reload speed")
        end
    end
    -- DEBUG (temporary): log every reload anim event and the end of a crossbow reload
    if Q.DEBUG and ISReloadWeaponAction.animEvent then
        local origEv = ISReloadWeaponAction.animEvent
        ISReloadWeaponAction.animEvent = function(self, event, parameter)
            if Q.isCrossbow(self.gun) then
                JC.log("DEBUG reload anim event: " .. tostring(event) .. " " .. tostring(parameter)
                    .. " ammo=" .. tostring(JC.try(self.gun, "getCurrentAmmoCount")))
            end
            return origEv(self, event, parameter)
        end
        local origPerf = ISReloadWeaponAction.perform
        ISReloadWeaponAction.perform = function(self, ...)
            if Q.isCrossbow(self.gun) then
                JC.log("DEBUG reload done, ammo=" .. tostring(JC.try(self.gun, "getCurrentAmmoCount")))
            end
            return origPerf(self, ...)
        end
        local origStop = ISReloadWeaponAction.stop
        ISReloadWeaponAction.stop = function(self, ...)
            if Q.isCrossbow(self.gun) then
                JC.log("DEBUG reload STOPPED, ammo=" .. tostring(JC.try(self.gun, "getCurrentAmmoCount")))
            end
            return origStop(self, ...)
        end
    end
    -- Safety net: a crossbow reload can never get stuck. The game loads the bolt on the
    -- animation's "loadFinished" event (solo) or on the server's own timer (MP). If that event
    -- has not come WATCHDOG x the expected time after the start (e.g. the animation was
    -- replaced or cut), the bolt is loaded here, the same way (solo / server only).
    local origStart, origUpdate = ISReloadWeaponAction.start, ISReloadWeaponAction.update
    local origEv2 = ISReloadWeaponAction.animEvent
    if origStart and origUpdate and origEv2 then
    ISReloadWeaponAction.start = function(self, ...)
        self.jcStart = getTimestampMs and getTimestampMs() or nil
        self.jcLoaded = false
        return origStart(self, ...)
    end
    ISReloadWeaponAction.animEvent = function(self, event, parameter)
        if event == "loadFinished" then
            self.jcLoaded = true
        end
        return origEv2(self, event, parameter)
    end
    ISReloadWeaponAction.update = function(self, ...)
        local r = origUpdate(self, ...)
        pcall(function()
            if self.jcLoaded or not self.jcStart or isClient() or not Q.isCrossbow(self.gun) then
                return
            end
            local rs = self.character:getVariableFloat("ReloadSpeed", 1.0)
            if rs <= 0 then rs = 1.0 end
            local due = Q.WATCHDOG * 590 / rs
            if getTimestampMs() - self.jcStart > due then
                self.jcLoaded = true
                JC.log("crossbow reload: no loadFinished from the animation after " .. math.floor(due) .. " ms, loading the bolt")
                self:loadAmmo()
            end
        end)
        return r
    end
    end
    Q.wrapped = true
    JC.log("reload hook installed (speed x" .. tostring(Q.SPEED) .. ")")
    return true
end

-- ---------------------------------------------------------------------------- real bolts: no game hit
Q.SHORT_RANGE = 0.7
Q.RANGE = 25.0

function Q.real()
    return JC.optBool("RealBolts", true)
end

function Q.onSwing(character, weapon)
    if Q.isCrossbow(weapon) and Q.real() then
        JC.try(weapon, "setMaxRange", Q.SHORT_RANGE)
    end
end

function Q.onAttackFinished(character, weapon)
    if Q.isCrossbow(weapon) then
        JC.try(weapon, "setMaxRange", Q.RANGE)
    end
end

-- ---------------------------------------------------------------------------- R key
--- Can this player load a bolt now? Returns the crossbow or nil.
function Q.ready(player)
    if not player or JC.try(player, "isDead") then
        return nil
    end
    local gun = JC.try(player, "getPrimaryHandItem")
    if not Q.isCrossbow(gun) then
        return nil
    end
    if (JC.try(gun, "getCurrentAmmoCount") or 0) >= (JC.try(gun, "getMaxAmmo") or 1) then
        return nil
    end
    local queue = ISTimedActionQueue and ISTimedActionQueue.queues and ISTimedActionQueue.queues[player]
    if queue and #queue.queue > 0 then
        return nil
    end
    local inv = player:getInventory()
    local n = JC.try(inv, "getCountTypeRecurse", JC.Catalog.bolt) or 0
    if n < 1 then
        n = JC.try(inv, "getItemCountRecurse", JC.Catalog.module .. "." .. JC.Catalog.bolt) or 0
    end
    if n < 1 then
        return nil
    end
    return gun
end

function Q.onKey(key)
    local ok, err = pcall(function()
        if not getCore():isKey(KeybindId.RELOAD_WEAPON, key) then
            return
        end
        if UIManager.getSpeedControls() and UIManager.getSpeedControls():getCurrentGameSpeed() == 0 then
            return
        end
        local player = getSpecificPlayer(0)
        local gun = Q.ready(player)
        if Q.DEBUG and Q.isCrossbow(JC.try(player, "getPrimaryHandItem")) then
            JC.log("DEBUG R pressed: ready=" .. tostring(gun ~= nil))
        end
        if gun then
            ISReloadWeaponAction.BeginAutomaticReload(player, gun)
        end
    end)
    if not ok and not Q.keyErr then
        Q.keyErr = true
        JC.log("Crossbow quick reload (R) error: " .. tostring(err))
    end
end

if Events then
    if Events.OnGameBoot then
        Events.OnGameBoot.Add(Q.wrapSpeed)
    end
    if Events.OnServerStarted then
        Events.OnServerStarted.Add(Q.wrapSpeed)
    end
    if Events.OnGameStart then
        Events.OnGameStart.Add(Q.wrapSpeed)
    end
    if Events.OnWeaponSwing then
        Events.OnWeaponSwing.Add(function(c, w) pcall(Q.onSwing, c, w) end)
    end
    if Events.OnPlayerAttackFinished then
        Events.OnPlayerAttackFinished.Add(function(c, w) pcall(Q.onAttackFinished, c, w) end)
    end
    if isClient() or not isServer() then
        if Events.OnKeyStartPressed then
            Events.OnKeyStartPressed.Add(Q.onKey)
        end
        -- also on key up, in case key down was missed (safe: a loaded crossbow or a
        -- busy queue makes the second call do nothing)
        if Events.OnKeyPressed then
            Events.OnKeyPressed.Add(Q.onKey)
        end
    end
end

return Q
