-- Jamie's Crossbows - offline tests (server rules). Run: lua5.1 run_tests.lua
local H = dofile("harness.lua")
H.loadAll()
local JC = JamiesCrossbows
local N = JC.Net

local admin = H.newPlayer("Jamie", "admin", 100.5, 100.5, 0)
local mod = H.newPlayer("Moddy", "moderator", 101.5, 100.5, 0)
local joe = H.newPlayer("Joe", nil, 102.5, 100.5, 0)
H.online = {admin, mod, joe}

local function ask(player, command, args)
    H.ms = H.ms + 5000 -- past every rate limit
    H.clearSent()
    N.dispatchServer(player, command, args or {})
    for i = #H.sent, 1, -1 do
        local m = H.sent[i]
        if m.command == "result" and m.to == player then return m.args end
    end
    return nil
end

H.section("catalog")
do
    local Cat = JC.catalog()
    local X = JC.Server
    H.eq(#Cat.crossbows, 10, "all ten crossbows in the catalog")
    for _, c in ipairs(Cat.crossbows) do
        local d = JC.byId[c.id]
        H.ok(d and d.full == "JamiesCrossbows." .. c.id and JC.isCrossbow(H.newItem(d.full)), c.id .. " is a crossbow")
    end
    H.ok(not JC.isCrossbow(H.newItem("Base.HuntingRifle")), "a gun is not")
    H.ok(not JC.isCrossbow(nil), "nothing is not")
    local xid = Cat.crossbows[1].id
    local xdef = JC.byId[xid]
    -- 0.11.1: the shot drops the bolt where it lands (server), or breaks it
    SandboxVars.JamiesCrossbows.RealBolts = false   -- the game-shot mode
    local boltFull = Cat.module .. "." .. Cat.bolt
    local hunter = H.newPlayer("Hunter", nil, 10.5, 10.5, 0)
    hunter.dir = {1, 0}
    local xb = H.newItem(xdef.full)
    xb.getCurrentAmmoCount = function() return 1 end
    xb.getMaxRange = function() return 25 end
    xb.getID = function() return 777 end
    hunter.primary = xb
    for x = 10, 20 do H.square(x, 10, 0) end      -- an open corridor 10..20, nothing at 21: the edge
    X.onSwing(hunter, xb)
    local shot = X.onHitPoint(hunter, xb)
    H.ok(shot ~= nil and X.ticking, "a crossbow shot is pending and the resolver runs")
    local res, at = X.resolve(shot, 0.99)
    H.eq(res, "dropped", "a miss: the bolt drops")
    H.ok(at.x > 20 and at.x < 21, "at the last open square of its path (" .. string.format("%.1f", at.x) .. ")")
    local onFloor = 0
    for _, w in ipairs(H.squares["20,10,0"].world) do if w.item.full == boltFull then onFloor = onFloor + 1 end end
    H.eq(onFloor, 1, "one bolt on the floor there")
    H.squares["14,10,0"].blockedTo = {[H.squares["15,10,0"]] = true}    -- a wall between 14 and 15
    res, at = X.resolve({player = hunter, x = 10.5, y = 10.5, z = 0, dx = 1, dy = 0, range = 25, ticks = 0}, 0.99)
    H.ok(math.floor(at.x) == 14, "a wall stops it: it drops before the wall")
    H.squares["14,10,0"].blockedTo = nil
    H.eq((X.resolve({player = hunter, x = 10.5, y = 10.5, z = 0, dx = 1, dy = 0, range = 25, ticks = 0}, 0.0)), "broken",
        "a low roll breaks the bolt (20% chance)")
    H.ok(math.abs(X.breakChance(hunter) - 0.2) < 1e-9, "break chance 20% at Crossbow level 0")
    hunter.perks = {[Perks.Crossbow] = 10}
    H.ok(math.abs(X.breakChance(hunter) - 0.1) < 1e-9, "Crossbow level 10: half (10%)")
    hunter.perks = nil
    -- a hit in the same attack: the bolt drops at the target, Crossbow XP
    H.xp = {}
    local zed = {getX = function() return 13.5 end, getY = function() return 10.5 end, getZ = function() return 0 end}
    X.onSwing(hunter, xb)
    local s2 = X.onHitPoint(hunter, xb)
    X.onHit(hunter, zed, xb)
    H.ok(s2.hit and s2.hit.x == 13.5, "the hit is remembered for this shot")
    H.ok(#H.xp == 1 and H.xp[1].perk == Perks.Crossbow and H.xp[1].n == X.XP_HIT, "Crossbow XP for a hit")
    X.tick()
    H.ok(X.pending["Hunter#6"] == nil, "a shot with a hit resolves on the next tick, once")
    local atZed = 0
    for _, w in ipairs(H.squares["13,10,0"].world) do if w.item.full == boltFull then atZed = atZed + 1 end end
    H.ok(atZed <= 1, "at most one bolt at the target (it may have broken)")
    for _ = 1, X.RESOLVE_TICKS + 1 do X.tick() end
    H.ok(not X.ticking, "nothing pending: the resolver removed itself (no per-tick work)")
    -- a dry click: no bolt
    xb.getCurrentAmmoCount = function() return 0 end
    X.onSwing(hunter, xb)
    H.eq(X.onHitPoint(hunter, xb), nil, "an empty crossbow: no bolt leaves it")
    -- not a crossbow
    hunter.primary = H.newItem("Base.Katana")
    H.eq(X.onHitPoint(hunter, hunter.primary), nil, "a blade swing makes no bolt")
    -- kill XP
    H.xp = {}
    hunter.primary = xb
    X.onZombieDead({getAttackedBy = function() return hunter end})
    H.ok(#H.xp == 1 and H.xp[1].n == X.XP_KILL, "Crossbow XP for a kill")
end

H.section("admin give")
do
    local Cat = JC.catalog()
    local xid = Cat.crossbows[1].id
    local before = admin.inv:count(Cat.module .. "." .. Cat.bolt)
    local rr = ask(admin, "give", {id = Cat.bolt})
    H.ok(rr and rr.ok and rr.key == "IGUI_JC_Given", "admin gives bolts")
    H.eq(admin.inv:count(Cat.module .. "." .. Cat.bolt) - before, 10, "a bundle of 10")
    rr = ask(joe, "give", {id = Cat.bolt})
    H.ok(rr and not rr.ok and rr.key == "IGUI_JC_NotStaff", "a player can't give himself bolts")
    H.eq(joe.inv:count(Cat.module .. "." .. Cat.bolt), 0, "and gets none")
    rr = ask(mod, "give", {id = xid})
    H.ok(rr and not rr.ok, "a moderator can't by default (StaffLevel 1)")
    SandboxVars.JamiesCrossbows.StaffLevel = 2
    rr = ask(mod, "give", {id = xid})
    H.ok(rr and rr.ok, "StaffLevel 2: moderators can")
    SandboxVars.JamiesCrossbows.StaffLevel = nil
    rr = ask(admin, "give", {id = xid})
    H.ok(rr and rr.ok and admin.inv:count(JC.byId[xid].full) == 1, "admin gives the crossbow")
    rr = ask(admin, "give", {id = "Base.Axe"})
    H.ok(rr and not rr.ok, "anything else: refused")
end

H.section("Crossbows: real bolts")
do
    local Cat = JC.catalog()
    local X = JC.Server
    SandboxVars.JamiesCrossbows.RealBolts = nil     -- default: on
    H.ok(X.real(), "real bolts on by default")
    local boltFull = Cat.module .. "." .. Cat.bolt
    for x = 30, 60 do H.square(x, 30, 0) end                 -- an open lane 30..60
    local p = H.newPlayer("Archer2", nil, 30.5, 30.5, 0)
    p.dir = {1, 0}
    local xb = H.newItem(JC.byId[Cat.crossbows[3].id].full)
    xb.getCurrentAmmoCount = function() return 1 end
    xb.getMinDamage = function() return 1.4 end
    xb.getMaxDamage = function() return 2.2 end
    xb.getCriticalChance = function() return 35 end
    xb.getCritDmgMultiplier = function() return 4 end
    xb.getID = function() return 991 end
    p.primary = xb
    local function zombie(x, y, health)
        local z = {class = "IsoZombie", x = x, y = y, z = 0, health = health or 1.5, dead = false}
        function z:getX() return self.x end
        function z:getY() return self.y end
        function z:getZ() return self.z end
        function z:isDead() return self.dead end
        function z:getHealth() return self.health end
        function z:setHealth(h) self.health = h end
        function z:setAttackedBy(a) self.by = a end
        function z:setStaggerBack(b) self.stagger = b end
        function z:Kill(w, a) self.dead = true self.killedWith = w self.killedBy = a end
        local sq = H.squares[math.floor(x) .. "," .. math.floor(y) .. ",0"] or H.square(math.floor(x), math.floor(y), 0)
        sq.moving = sq.moving or {}
        table.insert(sq.moving, z)
        return z
    end
    -- the line
    local tr = X.trace({x = 30.8, y = 30.5, z = 0, dx = 1, dy = 0, range = 25})
    H.eq(tr.kind, "range", "an empty lane: the bolt flies its whole range")
    H.ok(math.abs(tr.dist - 25) < 1e-9 and tr.x > 55, "25 tiles")
    local zed = zombie(40.5, 30.6, 1.5)
    local far = zombie(45.5, 30.5, 1.5)
    tr = X.trace({x = 30.8, y = 30.5, z = 0, dx = 1, dy = 0, range = 25})
    H.ok(tr.kind == "hit" and tr.target == zed, "it stops at the FIRST zombie on its line")
    local side = zombie(35.5, 31.9, 1.5)
    tr = X.trace({x = 30.8, y = 30.5, z = 0, dx = 1, dy = 0, range = 25})
    H.ok(tr.target == zed, "a zombie beside the line is not hit")
    H.squares["37,30,0"].blockedTo = {[H.squares["38,30,0"]] = true}
    tr = X.trace({x = 30.8, y = 30.5, z = 0, dx = 1, dy = 0, range = 25})
    H.ok(tr.kind == "wall" and math.floor(tr.x) == 37, "a wall stops it before the zombie behind it")
    H.squares["37,30,0"].blockedTo = nil
    -- spread
    H.ok(math.abs(X.spread(p) - X.SPREAD_MAX) < 1e-9, "spread at Aiming 0: " .. X.SPREAD_MAX .. " degrees")
    p.perks = {[Perks.Aiming] = 10}
    H.ok(X.spread(p) < 1.0, "Aiming 10: under 1 degree")
    p.perks = nil
    -- the shot: everyone is told, the hit lands after the flight time
    H.clearSent()
    H.xp = {}
    p.perks = {[Perks.Aiming] = 10}                           -- a steady hand: 0.5 degrees
    X.onSwing(p, xb)
    local f = X.onHitPoint(p, xb)
    p.perks = nil
    H.ok(f and f.tr.kind == "hit" and f.tr.target == zed, "the shot flies at the zombie")
    local told = nil
    for _, m in ipairs(H.sent) do if m.command == "boltFly" and m.to == "all" then told = m.args end end
    H.ok(told and told.kind == "hit" and told.ms > 300 and told.ms < 600, "every client is told once (flight " .. tostring(told and told.ms) .. " ms)")
    H.ok(not zed.by, "nothing happens before the bolt arrives")
    X.tick()
    H.ok(not zed.by and X.flying[f.id], "still in the air")
    H.ms = H.ms + told.ms + 1
    X.tick()
    H.ok(zed.by == p, "it arrives: the zombie is hit by the shooter")
    H.ok(zed.dead or zed.health < 1.5, "and damaged (" .. (zed.dead and "killed" or string.format("%.2f left", zed.health)) .. ")")
    H.ok(#H.xp >= 1 and H.xp[1].perk == Perks.Crossbow, "Crossbow XP for the hit")
    H.ok(X.flying[f.id] == nil, "resolved once")
    -- point blank: the game's own hit (zombie inside the cut range) gives no second XP
    H.xp = {}
    X.onHit(p, zed, xb)
    H.eq(#H.xp, 0, "real bolts: the game's own point-blank hit gives no extra Crossbow XP")
    -- damage numbers
    local z2 = zombie(50.5, 30.5, 20)
    H.eq(X.damage(p, xb, z2, 0, 99), "hurt", "a strong zombie: hurt")
    H.ok(math.abs(z2.health - (20 - 1.4)) < 1e-9 and z2.stagger, "min damage 1.4, it staggers")
    X.damage(p, xb, z2, 1, 0)
    H.ok(math.abs(z2.health - (20 - 1.4 - 2.2 * 4)) < 1e-9, "a crit: max 2.2 x4")
    local z3 = zombie(51.5, 30.5, 1.0)
    H.eq(X.damage(p, xb, z3, 0.5, 99), "killed", "health runs out: killed")
    H.ok(z3.killedBy == p and z3.killedWith == xb, "Kill(weapon, shooter): the game's own death (OnZombieDead, XP)")
    H.eq(X.damage(p, xb, z3, 0.5, 99), "gone", "a dead zombie is not hit again")
    -- a miss lands a bolt
    for _ = 1, 3 do X.tick() end
    H.ok(not X.ticking, "nothing in the air: the resolver stopped")
    SandboxVars.JamiesCrossbows.RealBolts = false
    H.ok(not X.real(), "the sandbox option turns it off")
    SandboxVars.JamiesCrossbows.RealBolts = nil
    -- shared: the game's own hit range is cut only for the shot
    local Q = JC.Reload
    local range = 25
    xb.setMaxRange = function(_, r) range = r end
    Q.onSwing(p, xb)
    H.eq(range, Q.SHORT_RANGE, "at the swing the game's range is arm's length (no game hit, tiny streak)")
    Q.onAttackFinished(p, xb)
    H.eq(range, 25, "and back to 25 after the shot")
    SandboxVars.JamiesCrossbows.RealBolts = false
    Q.onSwing(p, xb)
    H.eq(range, 25, "real bolts off: the game's range is kept")
    SandboxVars.JamiesCrossbows.RealBolts = nil
    local _ = boltFull
end

H.section("Crossbow quick reload: R and speed")
do
    local Cat = JC.catalog()
    local Q = JC.Reload
    local xdef = JC.byId[Cat.crossbows[2].id]
    local p = H.newPlayer("Loader", nil, 5, 5, 0)
    local xb = H.newItem(xdef.full)
    local ammo = 0
    xb.getCurrentAmmoCount = function() return ammo end
    xb.getMaxAmmo = function() return 1 end
    p.primary = xb
    local queued = {}
    ISTimedActionQueue = {queues = {}}
    ISReloadWeaponAction = {BeginAutomaticReload = function(pl, g) queued[#queued + 1] = g end,
                            setReloadSpeed = function(ch) ch:setVariable("ReloadSpeed", 0.8) end}
    KeybindId = {RELOAD_WEAPON = "R"}
    getCore = function() return {isKey = function(_, id, key) return key == id end} end
    UIManager = {getSpeedControls = function() return nil end}
    local oldGSP = getSpecificPlayer
    getSpecificPlayer = function() return p end
    Q.onKey("R")
    H.eq(#queued, 0, "R with no bolts: nothing (the game's radial menu still works)")
    p.inv:AddItem(H.newItem(Cat.module .. "." .. Cat.bolt))
    Q.onKey("E")
    H.eq(#queued, 0, "another key: nothing")
    Q.onKey("R")
    H.ok(#queued == 1 and queued[1] == xb, "R with a bolt: the game's automatic reload starts at once")
    ammo = 1
    Q.onKey("R")
    H.eq(#queued, 1, "R when loaded: nothing")
    ammo = 0
    ISTimedActionQueue.queues[p] = {queue = {1}}
    Q.onKey("R")
    H.eq(#queued, 1, "R while busy: nothing (no double reload)")
    ISTimedActionQueue.queues[p] = nil
    p.primary = H.newItem("Base.Katana")
    Q.onKey("R")
    H.eq(#queued, 1, "R with a blade or a gun: left to the game")
    -- faster reload, crossbows only
    Q.wrapped = false
    H.ok(Q.wrapSpeed(), "reload speed hook installed")
    ISReloadWeaponAction.setReloadSpeed(p, false)
    H.ok(math.abs(p:getVariableFloat("ReloadSpeed", 0) - 0.8) < 1e-9, "not a crossbow: the game's speed")
    p.primary = xb
    ISReloadWeaponAction.setReloadSpeed(p, false)
    H.ok(math.abs(p:getVariableFloat("ReloadSpeed", 0) - 0.8 * Q.SPEED) < 1e-9, "crossbow: x" .. Q.SPEED .. " reload speed")
    H.ok(not Q.wrapSpeed(), "hook installed only once")
    ISTimedActionQueue, ISReloadWeaponAction, KeybindId, getCore, UIManager, getSpecificPlayer = nil, nil, nil, nil, nil, oldGSP
end

H.done()
