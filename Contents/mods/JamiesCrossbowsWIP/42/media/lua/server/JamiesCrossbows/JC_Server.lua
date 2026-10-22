-- Jamie's Crossbows - the server side: the bolt in flight, the hit, where it lands,
-- Crossbow skill XP, the admin give (server only; in solo the same code runs in the one game).
--
-- REAL BOLTS (sandbox RealBolts, on by default). The crossbow is an aimed firearm for
-- holding, aiming, firing, ammunition and reloading (AmmoType jamiescrossbows:crossbow_bolt,
-- media/registries.lua), but the game's own hit test does not decide: its range is cut to
-- arm's length for the moment of the shot (shared/JC_Reload.lua), so the game finds no
-- target and its bullet streak is a few centimetres. Here, at the shot (the game's
-- OnWeaponSwingHitPoint for a crossbow that held a bolt; the ammo count is read at
-- OnWeaponSwing, before it):
--   * the bolt's line: the shooter's facing, with a small random spread (less with Aiming)
--   * it flies along it at X.SPEED tiles a second and stops at the FIRST zombie within
--     X.HIT_RADIUS of the line, or before the first wall / closed door, or at its range
--   * every client is told once ("boltFly"): it draws the 3D bolt flying (client/JC_Fx.lua)
--   * when the bolt arrives (flight time later) the server applies the hit: damage from the
--     crossbow's own Min/MaxDamage and crit, the zombie killed with Kill(weapon, shooter)
--     when its health runs out
--   * the bolt then drops where it landed (at the zombie's feet, before the wall, at the
--     end of its range), or breaks (sandbox BoltBreak, default 20%, -5% of that per
--     Crossbow skill level: 10% at level 10)
-- RealBolts OFF: the game's own instant hit; the bolt drops at the target (OnWeaponHitCharacter)
-- or at the end of the miss path.
-- Only the server decides; clients send nothing, so a bolt can't be duplicated by a
-- client. Each shot is resolved once. The resolver runs only while a shot is pending /
-- a bolt is in the air, then removes itself: no per-frame work while nobody shoots.
-- XP: Crossbow skill (media/perks.txt) +3 per hit, +2 more per kill with a crossbow,
-- +1 Aiming per real-bolt hit.

if isClient() and not isServer() then
    return
end

require "JamiesCrossbows/JC_Core"
require "JamiesCrossbows/JC_Net"

local JC = JamiesCrossbows
JC.Server = JC.Server or {}
local X = JC.Server
local Cat = JC.catalog()

X.RESOLVE_TICKS = 8        -- wait this many ticks for the hit of the same shot
X.STEP = 0.5               -- tiles per step of the miss path
X.XP_HIT, X.XP_KILL = 3, 2

X.pending = {}             -- player key -> {player, x, y, z, dx, dy, range, hit = {x, y, z}, ticks}
X.ammoBefore = {}          -- weapon id -> ammo count when the swing started
X.ticking = false

-- real bolts
X.SPEED = 24               -- tiles a second (about 10 tiles in 0.4 s: you see it go)
X.RANGE = 25               -- tiles
X.TRACE_STEP = 0.25
X.HIT_RADIUS = 0.45
X.SPREAD_MAX, X.SPREAD_MIN, X.SPREAD_PER_AIM = 5.0, 0.5, 0.45   -- degrees, either side
X.flying = {}              -- id -> {shot, tr, due}
X.nextId = 0

function X.real()
    return JC.optBool("RealBolts", true)
end

function X.isCrossbow(item)
    return JC.isCrossbow(item)
end

function X.perk()
    return Perks and Perks.Crossbow or nil
end

function X.level(player)
    local p = X.perk()
    if not p then
        return 0
    end
    return JC.try(player, "getPerkLevel", p) or 0
end

--- Chance (0-1) that a shot breaks the bolt, for this player.
function X.breakChance(player)
    local base = JC.optNum("BoltBreak", (Cat.boltBreak or 0.2) * 100, 0, 100) / 100
    local lvl = math.max(0, math.min(10, X.level(player)))
    return base * (1 - 0.05 * lvl)
end

local function xp(player, n)
    local p = X.perk()
    if p and n > 0 then
        pcall(addXp, player, p, n)
    end
end

local function key(player)
    return JC.username(player) .. "#" .. tostring(JC.try(player, "getOnlineID") or 0)
end

local function weaponId(w)
    return JC.try(w, "getID") or tostring(w)
end

-- ---------------------------------------------------------------------------- the shot
function X.onSwing(player, weapon)
    if X.isCrossbow(weapon) then
        JC.log("DEBUG shot swing: ammo=" .. tostring(JC.try(weapon, "getCurrentAmmoCount")))
        X.ammoBefore[weaponId(weapon)] = JC.try(weapon, "getCurrentAmmoCount")
    end
end

function X.onHitPoint(player, weapon)
    if not player or not X.isCrossbow(weapon) then
        return nil
    end
    local id = weaponId(weapon)
    local before = X.ammoBefore[id]
    X.ammoBefore[id] = nil
    JC.log("DEBUG shot hit point: ammo before=" .. tostring(before) .. " now=" .. tostring(JC.try(weapon, "getCurrentAmmoCount"))
        .. " realBolts=" .. tostring(X.real()))
    if before ~= nil and before < 1 then
        return nil -- a dry click: no bolt left the crossbow
    end
    if X.real() then
        return X.launch(player, weapon)
    end
    local dx, dy = 0, 1
    pcall(function()
        local f = player:getForwardDirection()
        dx, dy = f:getX(), f:getY()
    end)
    local len = math.sqrt(dx * dx + dy * dy)
    if len < 1e-6 then
        dx, dy, len = 0, 1, 1
    end
    local shot = {player = player, x = player:getX(), y = player:getY(), z = player:getZ(), dx = dx / len, dy = dy / len,
                  range = JC.try(weapon, "getMaxRange") or 25, ticks = 0}
    X.pending[key(player)] = shot
    X.startResolver()
    return shot
end

function X.onHit(attacker, target, weapon)
    if not attacker or not target or not X.isCrossbow(weapon) then
        return
    end
    if X.real() then
        -- real bolts: the bolt decides the hit and gives the XP (X.impact). A zombie at
        -- point blank (MinRange 0.61 .. the cut range 0.7) can still take the game's own
        -- hit; it must not give the Crossbow XP a second time.
        return
    end
    local shot = X.pending[key(attacker)]
    if shot and not shot.hit then
        shot.hit = {x = target:getX(), y = target:getY(), z = target:getZ()}
    end
    xp(attacker, X.XP_HIT)
end

function X.onZombieDead(zombie)
    local killer = JC.try(zombie, "getAttackedBy")
    if killer and instanceof(killer, "IsoPlayer") and X.isCrossbow(JC.try(killer, "getPrimaryHandItem")) then
        xp(killer, X.XP_KILL)
    end
end

-- ---------------------------------------------------------------------------- where it lands
local function squareAt(x, y, z)
    local cell = getCell and getCell()
    return cell and cell:getGridSquare(math.floor(x), math.floor(y), math.floor(z)) or nil
end

local function open(sq)
    return sq ~= nil and JC.try(sq, "isSolid") ~= true and JC.try(sq, "isSolidTrans") ~= true
end

--- Walks the miss path; returns the last reachable point {x, y, z}.
function X.missPoint(shot)
    local x, y, z = shot.x, shot.y, shot.z
    local last = {x = x, y = y, z = z}
    local cur = squareAt(x, y, z)
    local t = X.STEP
    while t <= shot.range do
        local nx, ny = shot.x + shot.dx * t, shot.y + shot.dy * t
        local nsq = squareAt(nx, ny, z)
        if not open(nsq) then
            break
        end
        if cur and nsq ~= cur and JC.try(cur, "isBlockedTo", nsq) == true then
            break
        end
        cur = nsq
        last = {x = nx, y = ny, z = z}
        t = t + X.STEP
    end
    return last
end

--- Puts the bolt on the floor at p (or breaks it). Returns "dropped" | "broken" | "nosquare".
function X.land(shot, p, roll)
    local r = roll or (ZombRand(1000) / 1000)
    if r < X.breakChance(shot.player) then
        return "broken"
    end
    local sq = squareAt(p.x, p.y, p.z)
    if not sq then
        return "nosquare"
    end
    local fx, fy = p.x - math.floor(p.x), p.y - math.floor(p.y)
    sq:AddWorldInventoryItem(JC.boltFull(), fx, fy, 0)
    return "dropped"
end

function X.resolve(shot, roll)
    local p = shot.hit or X.missPoint(shot)
    return X.land(shot, p, roll), p
end

-- ---------------------------------------------------------------------------- real bolts 
local function nowMs()
    return getTimestampMs and getTimestampMs() or 0
end

local function aimLevel(player)
    return Perks and Perks.Aiming and (JC.try(player, "getPerkLevel", Perks.Aiming) or 0) or 0
end

--- Spread (degrees either side) for this player.
function X.spread(player)
    return math.max(X.SPREAD_MIN, X.SPREAD_MAX - X.SPREAD_PER_AIM * aimLevel(player))
end

local function zombiesNear(cx, cy, z, out)
    for ix = cx - 1, cx + 1 do
        for iy = cy - 1, cy + 1 do
            local sq = squareAt(ix, iy, z)
            local list = sq and JC.try(sq, "getMovingObjects")
            if list then
                for i = 0, list:size() - 1 do
                    local o = list:get(i)
                    if o and not out[o] and instanceof(o, "IsoZombie") and not JC.try(o, "isDead") then
                        out[o] = true
                        out[#out + 1] = o
                    end
                end
            end
        end
    end
end

--- Follows the bolt's line from the shot. Returns {kind = "hit"|"wall"|"range", x, y, dist, target}.
function X.trace(shot)
    local z = math.floor(shot.z)
    local cur = squareAt(shot.x, shot.y, z)
    local last = {x = shot.x, y = shot.y}
    local seen, curKey = {}, nil
    local t = X.TRACE_STEP
    while t <= shot.range do
        local px, py = shot.x + shot.dx * t, shot.y + shot.dy * t
        local nsq = squareAt(px, py, z)
        if not open(nsq) or (cur and nsq ~= cur and JC.try(cur, "isBlockedTo", nsq) == true) then
            return {kind = "wall", x = last.x, y = last.y, dist = t - X.TRACE_STEP}
        end
        local cx, cy = math.floor(px), math.floor(py)
        local key = cx * 100000 + cy
        if key ~= curKey then
            curKey = key
            zombiesNear(cx, cy, z, seen)
        end
        for i = 1, #seen do
            local o = seen[i]
            if o then
                local ox, oy = o:getX() - px, o:getY() - py
                if ox * ox + oy * oy <= X.HIT_RADIUS * X.HIT_RADIUS then
                    return {kind = "hit", x = o:getX(), y = o:getY(), dist = t, target = o}
                end
            end
        end
        cur = nsq
        last = {x = px, y = py}
        t = t + X.TRACE_STEP
    end
    return {kind = "range", x = last.x, y = last.y, dist = shot.range}
end

function X.launch(player, weapon, rollSpread)
    local dx, dy = 0, 1
    pcall(function()
        local f = player:getForwardDirection()
        dx, dy = f:getX(), f:getY()
    end)
    local len = math.sqrt(dx * dx + dy * dy)
    if len < 1e-6 then
        dx, dy, len = 0, 1, 1
    end
    local s = X.spread(player)
    local a = math.atan2(dy, dx) + math.rad(rollSpread or ((ZombRand(2001) / 1000 - 1) * s))
    dx, dy = math.cos(a), math.sin(a)
    local shot = {player = player, weapon = weapon, x = player:getX() + dx * 0.3, y = player:getY() + dy * 0.3,
                  z = player:getZ(), dx = dx, dy = dy, range = X.RANGE}
    local tr = X.trace(shot)
    X.nextId = X.nextId + 1
    local ms = math.floor(math.max(0.05, tr.dist / X.SPEED) * 1000)
    local f = {id = X.nextId, shot = shot, tr = tr, due = nowMs() + ms}
    X.flying[f.id] = f
    JC.Net.broadcast("boltFly", {id = f.id, x0 = shot.x, y0 = shot.y, z = math.floor(shot.z), x1 = tr.x, y1 = tr.y,
                                 kind = tr.kind, ms = ms})
    X.startResolver()
    return f
end

--- The bolt reached a zombie: damage (the crossbow's own numbers), maybe a kill.
--- Returns "killed" | "hurt" | "gone".
function X.damage(player, weapon, zombie, roll, critRoll)
    if not zombie or JC.try(zombie, "isDead") then
        return "gone"
    end
    local mn = JC.try(weapon, "getMinDamage") or 1.4
    local mx = JC.try(weapon, "getMaxDamage") or 2.2
    local dmg = mn + (mx - mn) * (roll or (ZombRand(1001) / 1000))
    local crit = (JC.try(weapon, "getCriticalChance") or 0) + 2 * aimLevel(player)
    if (critRoll or ZombRand(100)) < crit then
        dmg = dmg * (JC.try(weapon, "getCritDmgMultiplier") or 1)
    end
    pcall(zombie.setAttackedBy, zombie, player)
    local h = (JC.try(zombie, "getHealth") or 1) - dmg
    if h <= 0 then
        local ok = pcall(zombie.Kill, zombie, weapon, player)
        if not ok then
            pcall(zombie.setHealth, zombie, 0)
        end
        return "killed"
    end
    pcall(zombie.setHealth, zombie, h)
    pcall(zombie.setStaggerBack, zombie, true)
    return "hurt"
end

function X.impact(f)
    local shot, tr = f.shot, f.tr
    local p = {x = tr.x, y = tr.y, z = math.floor(shot.z)}
    if tr.kind == "hit" and tr.target then
        local zed = tr.target
        if not JC.try(zed, "isDead") then
            p = {x = zed:getX(), y = zed:getY(), z = math.floor(zed:getZ())}
        end
        local res = X.damage(shot.player, shot.weapon, zed)
        if res ~= "gone" then
            xp(shot.player, X.XP_HIT)
            if Perks and Perks.Aiming then
                pcall(addXp, shot.player, Perks.Aiming, 1)
            end
        end
    end
    return X.land(shot, p), p
end

-- ---------------------------------------------------------------------------- the short-lived resolver
function X.tick()
    local left = 0
    local now = nowMs()
    for id, f in pairs(X.flying) do
        if now >= f.due then
            X.flying[id] = nil
            local ok, err = pcall(X.impact, f)
            if not ok and not X.errorLogged then
                X.errorLogged = true
                JC.log("Crossbow bolt impact error: " .. tostring(err))
            end
        else
            left = left + 1
        end
    end
    for k, shot in pairs(X.pending) do
        shot.ticks = shot.ticks + 1
        if shot.hit or shot.ticks >= X.RESOLVE_TICKS then
            X.pending[k] = nil
            local ok, err = pcall(X.resolve, shot)
            if not ok and not X.errorLogged then
                X.errorLogged = true
                JC.log("Crossbow bolt landing error: " .. tostring(err))
            end
        else
            left = left + 1
        end
    end
    if left == 0 then
        X.stopResolver()
    end
end

function X.startResolver()
    if not X.ticking and Events and Events.OnTick then
        X.ticking = true
        Events.OnTick.Add(X.tick)
    end
end

function X.stopResolver()
    if X.ticking and Events and Events.OnTick then
        Events.OnTick.Remove(X.tick)
    end
    X.ticking = false
end

local function guarded(fn)
    return function(a, b, c, d)
        local ok, err = pcall(fn, a, b, c, d)
        if not ok and not X.errorLogged then
            X.errorLogged = true
            JC.log("Crossbow error: " .. tostring(err))
        end
    end
end

if Events then
    if Events.OnWeaponSwing then
        Events.OnWeaponSwing.Add(guarded(X.onSwing))
    end
    if Events.OnWeaponSwingHitPoint then
        Events.OnWeaponSwingHitPoint.Add(guarded(X.onHitPoint))
    end
    if Events.OnWeaponHitCharacter then
        Events.OnWeaponHitCharacter.Add(guarded(X.onHit))
    end
    if Events.OnZombieDead then
        Events.OnZombieDead.Add(guarded(X.onZombieDead))
    end
end

-- ---------------------------------------------------------------------------- admin: give
--- Gives a crossbow or a bundle of bolts. Staff only (sandbox StaffLevel), checked here.
function X.give(player, args)
    local id = tostring(args and args.id or "")
    local inv = player:getInventory()
    local full, n = nil, 1
    if id == Cat.bolt then
        full, n = JC.boltFull(), Cat.boltBundle or 10
    elseif JC.byId[id] then
        full = JC.byId[id].full
    else
        JC.Net.send(player, "result", {ok = false, key = "IGUI_JC_Failed"})
        return 0
    end
    local given = 0
    for _ = 1, n do
        local item = instanceItem(full)
        if item then
            inv:AddItem(item)
            if isServer() then
                sendAddItemToContainer(inv, item)
            end
            given = given + 1
        end
    end
    JC.log("AUDIT | " .. JC.username(player) .. " | give | " .. given .. "x " .. full)
    JC.Net.send(player, "result", {ok = given > 0, key = "IGUI_JC_Given", name = full, count = given})
    return given
end

JC.Net.handle("give", X.give, {staff = true})

return X
