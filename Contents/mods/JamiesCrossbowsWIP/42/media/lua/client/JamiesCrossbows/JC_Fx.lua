-- Jamie's Crossbows - a crossbow shot without the gun flash (client).
--
-- For every aimed firearm shot 42.21 puts a short orange light (a muzzle flash, radius 18,
-- a few frames) on the shooter's square (EffectsManager.startMuzzleFlash; read from the
-- jar). A crossbow has no powder, so here, on each client, that light is taken away again
-- when the shooter holds a crossbow: right at the shot (OnWeaponSwingHitPoint;
-- for other players the game adds the light before this event) and for the next 3 ticks
-- (for your own shot the game adds it after the event). Removed with the game's own
-- IsoCell:removeLamppost. Only lights on the shooter's square with the flash's size and
-- colour are touched (never a lamp or a fire).
-- No flash model is drawn for the crossbows (their scripts have no MuzzleFlashModelKey).
-- The shot streak (tracer) is the game's own and can't be changed by a mod in 42.21
-- (IsoBulletTracerEffects is not exposed to Lua); with real bolts it is cut to a few centimetres.
-- THE BOLT YOU SEE FLY. The server tells every client about each real bolt once
-- ("boltFly": start, end, flight time, what it hits). Here a look-only bolt
-- (JC_CrossbowBoltFlying, the same glowing 3D bolt) is put on the floor of THIS game only
-- (never sent to the server) and moved along the line each tick, at chest height, turned
-- the way it flies; a bolt that flies its whole range sinks to the floor at the end. When
-- it arrives it is removed: the real bolt (or nothing, if it broke) is the server's.
-- On a hit, a little blood where it struck.
-- Runs only for a few ticks after a crossbow shot / while a bolt flies; nothing otherwise.

if isServer() and not isClient() then
    return
end

require "JamiesCrossbows/JC_Core"
require "JamiesCrossbows/JC_Reload"
require "JamiesCrossbows/JC_Net"

local JC = JamiesCrossbows
JC.Fx = JC.Fx or {}
local Fx = JC.Fx
local Q = JC.Reload

Fx.RADIUS = 18        -- EffectsManager.startMuzzleFlash: new IsoLightSource(x, y, z, 0.8f*n, 0.8f*n, 0.6f*n, 18, 6)
Fx.TICKS = 3
Fx.pending = {}       -- {x, y, z, ticks}
Fx.ticking = false

local function isFlash(light, x, y, z)
    if light:getX() ~= x or light:getY() ~= y or light:getZ() ~= z or light:getRadius() ~= Fx.RADIUS then
        return false
    end
    local r, g, b = light:getR(), light:getG(), light:getB()
    if r <= 0 then
        return false
    end
    return math.abs(g - r) < 0.001 and math.abs(b / r - 0.75) < 0.01
end

--- Removes the muzzle-flash light(s) at a square; returns how many.
function Fx.clear(x, y, z)
    local cell = getCell and getCell()
    if not cell then
        return 0
    end
    local list = cell:getLamppostPositions()
    local found = {}
    for i = list:size() - 1, 0, -1 do
        local l = list:get(i)
        if l and isFlash(l, x, y, z) then
            found[#found + 1] = l
        end
    end
    for _, l in ipairs(found) do
        cell:removeLamppost(l)
    end
    return #found
end

function Fx.tick()
    local left = 0
    for k, p in pairs(Fx.pending) do
        Fx.clear(p.x, p.y, p.z)
        p.ticks = p.ticks + 1
        if p.ticks >= Fx.TICKS then
            Fx.pending[k] = nil
        else
            left = left + 1
        end
    end
    if left == 0 and Fx.ticking then
        Fx.ticking = false
        Events.OnTick.Remove(Fx.tick)
    end
end

function Fx.onShot(character, weapon)
    if not character or not Q.isCrossbow(weapon) then
        return
    end
    local x, y, z = math.floor(character:getX()), math.floor(character:getY()), math.floor(character:getZ())
    Fx.clear(x, y, z)
    Fx.pending[x .. "," .. y .. "," .. z] = {x = x, y = y, z = z, ticks = 0}
    if not Fx.ticking and Events and Events.OnTick then
        Fx.ticking = true
        Events.OnTick.Add(Fx.tick)
    end
end

-- ---------------------------------------------------------------------------- the flying bolt
Fx.FLY_ITEM = "JamiesCrossbows.JC_CrossbowBoltFlying"
Fx.HEIGHT = 0.45          -- height above the floor while it flies (world item z offset)
Fx.YAW_OFFSET = 0         -- degrees added to the facing (model lies along +X)
Fx.YAW_SIGN = 1           -- -1 if the bolt turns the wrong way (mirror image) in game
Fx.DROP_FROM = 0.55       -- a bolt that flies its whole range starts falling here (fraction of the flight)
Fx.flights = {}           -- id -> flight
Fx.flyTicking = false

local function nowMs()
    return getTimestampMs and getTimestampMs() or 0
end

local function sqAt(x, y, z)
    local cell = getCell and getCell()
    return cell and cell:getGridSquare(math.floor(x), math.floor(y), z) or nil
end

local function removeObj(f)
    if f.obj then
        local sq = JC.try(f.obj, "getSquare")
        if sq then
            pcall(sq.removeWorldObject, sq, f.obj)
        else
            pcall(f.obj.removeFromWorld, f.obj)
            pcall(f.obj.removeFromSquare, f.obj)
        end
        f.obj = nil
        f.sq = nil
    end
end

--- Where the bolt is at fraction t (0..1) of its flight: x, y, height.
function Fx.pos(f, t)
    local x = f.x0 + (f.x1 - f.x0) * t
    local y = f.y0 + (f.y1 - f.y0) * t
    local h = Fx.HEIGHT
    if f.kind == "range" and t > Fx.DROP_FROM then
        -- falls like a thrown thing (slow at first, faster near the floor), not down a ramp
        local u = (t - Fx.DROP_FROM) / (1 - Fx.DROP_FROM)
        h = Fx.HEIGHT * math.max(0, 1 - u * u)
    end
    return x, y, h
end

--- Moves the look-only bolt inside its square. NOT obj:setOffset: in 42.21 that also calls
--- sync(1), which in MP sends a SyncIsoObject for an object the server never had (by index,
--- so it could land on a real item) on every tick. setOffX/Y/Z only set the fields; the
--- redraw is asked for the same way setOffset does it (invalidateRenderChunkLevel(256)).
Fx.REDRAW = 256
Fx.DEBUG = true   -- TEMPORARY
local function shift(obj, ox, oy, h)
    -- solo: setOffset is safe (no network); MP: the quiet path, and if that ever fails
    -- (a Java call this build won't take) fall back to setOffset for the rest of the game
    if (isClient and isClient()) and not Fx.quietFailed then
        local ok, err = pcall(function()
            obj:setOffX(ox)
            obj:setOffY(oy)
            obj:setOffZ(h)
            obj:invalidateRenderChunkLevel(Fx.REDRAW)
        end)
        if ok then
            return
        end
        Fx.quietFailed = true
        JC.log("Flying bolt: quiet move not available (" .. tostring(err) .. "), using setOffset")
    end
    obj:setOffset(ox, oy, h)
end

local function place(f, x, y, h)
    local sq = sqAt(x, y, f.z)
    if not sq then
        removeObj(f)
        return
    end
    local ox, oy = x - math.floor(x), y - math.floor(y)
    if f.obj and f.sq == sq then
        shift(f.obj, ox, oy, h)
        return
    end
    removeObj(f)
    local item = f.item
    if not item then
        item = instanceItem(Fx.FLY_ITEM)
        f.item = item
    end
    if not item then
        return
    end
    pcall(item.setWorldZRotation, item, f.yaw)
    sq:AddWorldInventoryItem(item, ox, oy, h, false)
    f.obj = item:getWorldItem()
    f.sq = sq
    if f.obj then
        pcall(f.obj.setIgnoreRemoveSandbox, f.obj, true)
        pcall(f.obj.setWorldZRotation, f.obj, f.yaw)
    end
end

function Fx.flyTick()
    local now = nowMs()
    local left = 0
    for id, f in pairs(Fx.flights) do
        local t = f.ms > 0 and (now - f.start) / f.ms or 1
        if t >= 1 then
            removeObj(f)
            if f.kind == "hit" then
                local sq = sqAt(f.x1, f.y1, f.z)
                if sq and addBloodSplat then
                    pcall(addBloodSplat, sq, 3)
                end
            end
            Fx.flights[id] = nil
        else
            local ok, err = pcall(place, f, Fx.pos(f, t))
            if not ok then
                if not Fx.placeErr then
                    Fx.placeErr = true
                    JC.log("Flying bolt error: " .. tostring(err))
                end
                removeObj(f)
                Fx.flights[id] = nil
            else
                left = left + 1
            end
        end
    end
    if left == 0 and Fx.flyTicking then
        Fx.flyTicking = false
        Events.OnTick.Remove(Fx.flyTick)
    end
end

function Fx.fly(a)
    if type(a) ~= "table" or not a.x0 or not a.x1 then
        return nil
    end
    local f = {id = a.id, x0 = a.x0, y0 = a.y0, x1 = a.x1, y1 = a.y1, z = math.floor(a.z or 0), kind = a.kind,
               ms = tonumber(a.ms) or 0, start = nowMs()}
    f.yaw = Fx.YAW_SIGN * math.deg(math.atan2(f.y1 - f.y0, f.x1 - f.x0)) + Fx.YAW_OFFSET
    if Fx.DEBUG then
        JC.log("DEBUG bolt fly: id=" .. tostring(a.id) .. " kind=" .. tostring(a.kind) .. " ms=" .. tostring(a.ms)
            .. " from " .. tostring(a.x0) .. "," .. tostring(a.y0) .. " to " .. tostring(a.x1) .. "," .. tostring(a.y1))
    end
    if f.id ~= nil and Fx.flights[f.id] then
        removeObj(Fx.flights[f.id])
    end
    Fx.flights[f.id or (#Fx.flights + 1)] = f
    pcall(place, f, Fx.pos(f, 0))
    if not Fx.flyTicking and Events and Events.OnTick then
        Fx.flyTicking = true
        Events.OnTick.Add(Fx.flyTick)
    end
    return f
end

if JC.Net and JC.Net.on then
    JC.Net.on("boltFly", Fx.fly)
end

if Events and Events.OnWeaponSwingHitPoint then
    Events.OnWeaponSwingHitPoint.Add(function(character, weapon)
        local ok, err = pcall(Fx.onShot, character, weapon)
        if not ok and not Fx.errLogged then
            Fx.errLogged = true
            JC.log("Crossbow flash removal error: " .. tostring(err))
        end
    end)
end

return Fx
