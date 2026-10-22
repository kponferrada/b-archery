-- Jamie's Crossbows - offline tests (client side). Run: lua5.1 run_client.lua
local H = dofile("harness.lua")
H.loadAll()
H.mode = "client"
local JC = JamiesCrossbows
UIFont = {Small = 1, Medium = 2}
local TM = {getFontHeight = function(_, f) return 14 end,
            MeasureStringX = function(_, f, s) return #tostring(s) * 7 end}
function getTextManager() return TM end

H.section("crossbow: R without the wheel, bolt counter")
do
    local Cat = JC.catalog()
    local vanillaCalls = 0
    ISFirearmRadialMenu = {checkKey = function(key) vanillaCalls = vanillaCalls + 1 return true end}
    local drawn = {}
    ISEquippedItem = {render = function(self) end}
    KeybindId = {RELOAD_WEAPON = "R"}
    local oldCore = getCore
    getCore = function() return {isKey = function(_, id, key) return key == id end} end
    local p = H.newPlayer("Archer", nil, 5, 5, 0)
    local oldGSP = getSpecificPlayer
    getSpecificPlayer = function() return p end
    H.loaded["JamiesCrossbows/JC_Hud"] = nil
        local Hud = require("JamiesCrossbows/JC_Hud")
    H.ok(Hud.wheelWrapped and Hud.slotWrapped, "wheel and slot hooks installed")
    local gun = H.newItem("Base.HuntingRifle")
    p.primary = gun
    H.ok(ISFirearmRadialMenu.checkKey("R") == true, "a gun: R still opens the game's wheel")
    local xb = H.newItem(JC.byId[Cat.crossbows[1].id].full)
    local ammo = 1
    xb.getCurrentAmmoCount = function() return ammo end
    p.primary = xb
    H.ok(ISFirearmRadialMenu.checkKey("R") == false, "a crossbow: R never opens the wheel")
    H.ok(ISFirearmRadialMenu.checkKey("E") == true, "other keys untouched")
    for _ = 1, 3 do p.inv:AddItem(H.newItem(Cat.module .. "." .. Cat.bolt)) end
    local panel = {chr = p, mainHand = {x = 10, y = 10, width = 48, height = 48}}
    function panel:drawText(t, x, y, r, g, b, a) drawn[#drawn + 1] = {t = t, r = r, g = g, b = b, a = a} end
    ISEquippedItem.render(panel)
    H.eq(drawn[#drawn].t, "4", "counter: 1 loaded + 3 carried")
    H.ok(drawn[#drawn].b == 1, "white when loaded")
    ammo = 0
    H.ms = H.ms + 1000
    drawn = {}
    ISEquippedItem.render(panel)
    H.ok(drawn[#drawn].t == "3" and drawn[#drawn].b < 1, "amber when empty")
    p.primary = gun
    drawn = {}
    ISEquippedItem.render(panel)
    H.eq(#drawn, 0, "nothing drawn for a gun")
    getCore, getSpecificPlayer = oldCore, oldGSP
    ISFirearmRadialMenu, ISEquippedItem, KeybindId = nil, nil, nil
end

H.section("crossbow: no gun flash")
do
    local Cat = JC.catalog()
    H.loaded["JamiesCrossbows/JC_Fx"] = nil
    local Fx = require("JamiesCrossbows/JC_Fx")
    local function light(x, y, z, r, g, b, rad)
        return {getX = function() return x end, getY = function() return y end, getZ = function() return z end,
                getR = function() return r end, getG = function() return g end, getB = function() return b end,
                getRadius = function() return rad end}
    end
    local lamps = {}
    local list = {size = function() return #lamps end, get = function(_, i) return lamps[i + 1] end}
    local removed = {}
    local cell = {getLamppostPositions = function() return list end,
                  removeLamppost = function(_, l)
                      for i, x in ipairs(lamps) do if x == l then table.remove(lamps, i) end end
                      removed[#removed + 1] = l
                  end}
    local oldCell = getCell
    getCell = function() return cell end
    local flash = light(5, 5, 0, 0.8 * 0.5, 0.8 * 0.5, 0.6 * 0.5, 18)
    local lamp = light(5, 5, 0, 1, 1, 0.9, 18)          -- a real lamp on the same square
    local far = light(9, 9, 0, 0.4, 0.4, 0.3, 18)        -- a flash elsewhere (someone else's gun)
    lamps = {lamp, flash, far}
    local p = H.newPlayer("Shooter", nil, 5.5, 5.4, 0)
    local xb = H.newItem(JC.byId[Cat.crossbows[1].id].full)
    Fx.onShot(p, H.newItem("Base.HuntingRifle"))
    H.eq(#removed, 0, "a gun keeps its flash")
    Fx.onShot(p, xb)
    H.ok(#removed == 1 and removed[1] == flash, "a crossbow shot: its flash light is removed, the lamp and others stay")
    H.ok(Fx.ticking, "and it looks again for a few ticks (your own shot's light comes after the event)")
    lamps[#lamps + 1] = light(5, 5, 0, 0.16, 0.16, 0.12, 18)
    Fx.tick()
    H.eq(#removed, 2, "a flash added after the shot is removed on the next tick")
    Fx.tick() Fx.tick()
    H.ok(not Fx.ticking, "then it stops (no per-frame work)")
    H.eq(#lamps, 2, "lamp and the other flash untouched")
    getCell = oldCell
end

H.section("crossbow: the bolt you see fly")
do
    local Fx = JC.Fx
    local squares, adds, removes = {}, 0, 0
    local function fsq(x, y, z)
        local k = x .. "," .. y .. "," .. z
        if not squares[k] then
            local q = {x = x, y = y, items = {}}
            function q:AddWorldInventoryItem(item, ox, oy, h, transmit)
                adds = adds + 1
                H.ok(transmit == false, "the flying bolt is never sent to the server")
                local o = {item = item, sq = self, ox = ox, oy = oy, h = h}
                function o:setOffset() H.ok(false, "setOffset is not used (it syncs a local object in MP)") end
                function o:setOffX(a) self.ox = a end
                function o:setOffY(b) self.oy = b end
                function o:setOffZ(c) self.h = c end
                function o:invalidateRenderChunkLevel(fl) self.redraws = (self.redraws or 0) + 1 end
                function o:getSquare() return self.sq end
                function o:setWorldZRotation(r) self.yaw = r end
                function o:setIgnoreRemoveSandbox() end
                item.world = o
                self.items[o] = true
                return item
            end
            function q:removeWorldObject(o) removes = removes + 1 self.items[o] = nil end
            squares[k] = q
        end
        return squares[k]
    end
    local oldCell, oldII = getCell, instanceItem
    getCell = function() return {getGridSquare = function(_, x, y, z) return fsq(x, y, z) end} end
    instanceItem = function(full)
        return {full = full, getWorldItem = function(self) return self.world end, setWorldZRotation = function() end}
    end
    local f = Fx.fly({id = 7, x0 = 10.5, y0 = 10.5, z = 0, x1 = 20.5, y1 = 10.5, kind = "hit", ms = 400})
    H.ok(f and f.obj and f.item.full == "JamiesCrossbows.JC_CrossbowBoltFlying", "a look-only bolt appears at the start")
    H.ok(Fx.flyTicking and math.abs(f.yaw) < 1e-9, "it flies (facing east = 0 degrees)")
    H.ms = H.ms + 200
    Fx.flyTick()
    H.ok(f.obj and math.floor(f.obj.sq.x) == 15 and math.abs(f.obj.h - Fx.HEIGHT) < 1e-9, "half way after half the time, at chest height")
    local addsMid = adds
    H.ms = H.ms + 10
    Fx.flyTick()
    H.ok(adds - addsMid <= 1, "moving inside a square only shifts it")
    H.ms = H.ms + 300
    Fx.flyTick()
    H.ok(f.obj == nil and Fx.flights[7] == nil, "it arrives and is removed (the real bolt is the server's)")
    H.ok(not Fx.flyTicking, "nothing flying: no more ticks")
    local g = Fx.fly({id = 8, x0 = 10.5, y0 = 10.5, z = 0, x1 = 10.5, y1 = 35.5, kind = "range", ms = 1000})
    H.ok(math.abs(g.yaw - 90) < 1e-9, "facing follows the line (south = 90)")
    H.ms = H.ms + 900
    Fx.flyTick()
    H.ok(g.obj and g.obj.h < Fx.HEIGHT * 0.5, "at the end of its range it sinks to the floor")
    H.ms = H.ms + 200
    Fx.flyTick()
    for _, q in pairs(squares) do
        for _ in pairs(q.items) do H.ok(false, "a flying bolt was left behind") end
    end
    H.ok(adds > 0 and removes == adds, "every bolt shown was removed again (" .. adds .. ")")
    getCell, instanceItem = oldCell, oldII
end


H.section("admin menu")
do
    local Cat = JC.catalog()
    H.loaded["JamiesCrossbows/JC_Admin"] = nil
    local A = require("JamiesCrossbows/JC_Admin")
    local opts = {}
    local function menu()
        local m = {opts = {}}
        function m:addOption(name, target, fn) local o = {name = name, target = target, fn = fn} table.insert(self.opts, o) return o end
        function m:addSubMenu(o, sub) o.sub = sub end
        return m
    end
    ISContextMenu = {getNew = function() return menu() end}
    local me = H.newPlayer("Jamie", "admin", 1, 1, 0)
    local oldGP = getPlayer
    getPlayer = function() return me end
    local ctx = menu()
    A.fill(0, ctx, {}, false)
    H.ok(#ctx.opts == 1 and ctx.opts[1].sub, "staff: one admin entry with a submenu")
    local sub = ctx.opts[1].sub
    H.eq(#sub.opts, 11, "ten crossbows and the bolts")
    H.eq(sub.opts[11].target, Cat.bolt, "last: a bundle of bolts")
    H.clearSent()
    local oldReq = JC.Net.request
    local asked = nil
    JC.Net.request = function(c, a) asked = {c = c, a = a} end
    sub.opts[1].fn(sub.opts[1].target)
    H.ok(asked and asked.c == "give" and asked.a.id == Cat.crossbows[1].id, "picking one asks the server to give it")
    JC.Net.request = oldReq
    local joe = H.newPlayer("Joe", nil, 1, 1, 0)
    getPlayer = function() return joe end
    ctx = menu()
    A.fill(0, ctx, {}, false)
    H.eq(#ctx.opts, 0, "not staff: no admin entry")
    getPlayer = oldGP
end

H.done()
