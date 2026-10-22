-- Jamie's Crossbows - crossbow R key and bolt counter (client).
--
-- * R never opens the game's firearm wheel for a crossbow (that wheel shows a
--   pistol and bullets and, with "radial menu key toggle" on, stays open after a tap).
--   The game's own R handlers all ask ISFirearmRadialMenu.checkKey first; for the reload
--   key with a crossbow in the main hand it now says no, so only JC_CrossbowReload's
--   key-down reload runs. Guns keep the wheel.
-- * Bolt counter: on the main-hand slot (top left), a number = bolts left (the one in the
--   crossbow + all carried, bags too). White when loaded, amber when the crossbow is empty
--   (press R). Drawn with the slot; the inventory is counted at most twice a second.

if isServer() and not isClient() then
    return
end

require "JamiesCrossbows/JC_Core"
require "JamiesCrossbows/JC_Reload"
pcall(require, "ISUI/ISFirearmRadialMenu")
pcall(require, "ISUI/ISEquippedItem")

local JC = JamiesCrossbows
JC.Hud = JC.Hud or {}
local Hud = JC.Hud
local Q = JC.Reload

Hud.RECOUNT_MS = 500

local function isReloadKey(key)
    local ok, r = pcall(function()
        return getCore():isKey(KeybindId.RELOAD_WEAPON, key)
    end)
    return ok and r == true
end

-- ---------------------------------------------------------------------------- no wheel
function Hud.wrapWheel()
    if Hud.wheelWrapped or not ISFirearmRadialMenu or not ISFirearmRadialMenu.checkKey then
        return false
    end
    local orig = ISFirearmRadialMenu.checkKey
    ISFirearmRadialMenu.checkKey = function(key)
        if isReloadKey(key) then
            local p = getSpecificPlayer(0)
            if p and Q.isCrossbow(p:getPrimaryHandItem()) then
                return false
            end
        end
        return orig(key)
    end
    Hud.wheelWrapped = true
    return true
end

-- ---------------------------------------------------------------------------- bolt counter
--- Bolts left for this player and crossbow: loaded + carried; the second value is "loaded".
function Hud.count(player, gun)
    local loaded = JC.try(gun, "getCurrentAmmoCount") or 0
    local now = getTimestampMs and getTimestampMs() or 0
    local c = Hud.cache
    if not c or c.player ~= player or now - c.at >= Hud.RECOUNT_MS or now < c.at then
        local inv = player:getInventory()
        local n = JC.try(inv, "getCountTypeRecurse", JC.Catalog.bolt) or 0
        c = {player = player, at = now, carried = n}
        Hud.cache = c
    end
    return loaded + c.carried, loaded > 0
end

function Hud.draw(panel)
    local p = panel.chr
    local gun = p and p:getPrimaryHandItem()
    if not Q.isCrossbow(gun) or not panel.mainHand then
        return
    end
    local n, loaded = Hud.count(p, gun)
    local hand = panel.mainHand
    local text = tostring(n)
    local font = UIFont.Small
    local tm = getTextManager()
    local w = tm:MeasureStringX(font, text)
    local h = tm:getFontHeight(font)
    local x = hand.x + hand.width - w - 3
    local y = hand.y + hand.height - h - 1
    local r, g, b = 1, 1, 1
    if not loaded then
        r, g, b = 1, 0.7, 0.2
    end
    panel:drawText(text, x + 1, y + 1, 0, 0, 0, 0.9, font)
    panel:drawText(text, x, y, r, g, b, 1, font)
end

function Hud.wrapSlot()
    if Hud.slotWrapped or not ISEquippedItem or not ISEquippedItem.render then
        return false
    end
    local orig = ISEquippedItem.render
    ISEquippedItem.render = function(self)
        orig(self)
        local ok, err = pcall(Hud.draw, self)
        if not ok and not Hud.drawErr then
            Hud.drawErr = true
            JC.log("Crossbow bolt counter error: " .. tostring(err))
        end
    end
    Hud.slotWrapped = true
    return true
end

function Hud.install()
    Hud.wrapWheel()
    Hud.wrapSlot()
end

Hud.install()
if Events and Events.OnGameStart then
    Events.OnGameStart.Add(Hud.install)
end

return Hud
