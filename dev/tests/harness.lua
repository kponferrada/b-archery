-- Jamie's Crossbows - test harness: stand-ins for the game calls the mod makes.
-- Not part of the mod (dev/ is never uploaded).
--
-- What this proves: the mod's own rules and its server checks.
-- What it cannot prove: that the game behaves like these stand-ins. The
-- in-game checklist is docs/TEST_PLAN.md.

local H = {}
H.ROOT = os.getenv("JC_ROOT") or "../../Contents/mods/JamiesCrossbowsWIP/42/media/lua"

-- Kahlua lacks these: make any use of them fail here first.
unpack = unpack or table.unpack
next = nil
string.rep = nil
loadstring = nil

H.passed, H.failed = 0, 0
function H.ok(c, name)
    if c then
        H.passed = H.passed + 1
    else
        H.failed = H.failed + 1
        print("FAIL: " .. tostring(name))
    end
end
function H.eq(a, b, name)
    H.ok(a == b, tostring(name) .. " (got " .. tostring(a) .. ", want " .. tostring(b) .. ")")
end
function H.near(a, b, tol, name)
    H.ok(type(a) == "number" and math.abs(a - b) <= tol, tostring(name) .. " (got " .. tostring(a) .. ", want " .. tostring(b) .. ")")
end
function H.section(s)
    print("-- " .. s)
end
function H.done()
    print(string.format("tests: %d passed, %d failed", H.passed, H.failed))
    if H.failed > 0 then
        os.exit(1)
    end
end

-- ---------------------------------------------------------------- side and require
H.mode = "server"
function isServer() return H.mode == "server" end
function isClient() return H.mode == "client" end

H.loaded = {}
function require(name)
    if H.loaded[name] then
        return H.loaded[name]
    end
    local path = H.ROOT .. "/shared/" .. name .. ".lua"
    local f = io.open(path)
    if not f then
        path = H.ROOT .. "/server/" .. name .. ".lua"
        f = io.open(path)
    end
    if not f then
        path = H.ROOT .. "/client/" .. name .. ".lua"
        f = io.open(path)
    end
    if not f then
        H.loaded[name] = true -- vanilla files (Items/ProceduralDistributions ...) are stand-ins
        return true
    end
    f:close()
    H.loaded[name] = true
    local r = dofile(path)
    if r ~= nil then
        H.loaded[name] = r
    end
    return H.loaded[name]
end

-- ---------------------------------------------------------------- time, random, text
H.ms = 1000000
function getTimestampMs() return H.ms end
function getTimestamp() return math.floor(H.ms / 1000) end
H.rng = 12345
function ZombRand(n)
    H.rng = (H.rng * 1103515245 + 12345) % 2147483648
    return H.rng % n
end
function getText(key, a, b, c)
    local s = key
    if a then s = s .. "|" .. tostring(a) end
    if b then s = s .. "|" .. tostring(b) end
    return s
end

-- ---------------------------------------------------------------- events
H.events = {}
Events = setmetatable({}, {__index = function(t, name)
    local e = {list = {}}
    function e.Add(fn) table.insert(e.list, fn) end
    function e.Remove(fn)
        for i, f in ipairs(e.list) do
            if f == fn then table.remove(e.list, i) return end
        end
    end
    rawset(t, name, e)
    return e
end})
function H.fire(name, ...)
    local e = rawget(Events, name)
    if e then
        for _, fn in ipairs(e.list) do fn(...) end
    end
end
function triggerEvent(name, ...) H.fire(name, ...) end

-- ---------------------------------------------------------------- sandbox, ModData, files
SandboxVars = {JamiesCrossbows = {}}
H.globalMD = {}
ModData = {}
function ModData.getOrCreate(k)
    H.globalMD[k] = H.globalMD[k] or {}
    return H.globalMD[k]
end
H.fileLines = {}
function getFileWriter(name, a, b)
    return {write = function(_, s) table.insert(H.fileLines, s) end, close = function() end}
end

-- ---------------------------------------------------------------- network
H.sent = {}
function sendServerCommand(a, b, c, d)
    if type(a) == "string" then
        table.insert(H.sent, {to = "all", module = a, command = b, args = c})
    else
        table.insert(H.sent, {to = a, module = b, command = c, args = d})
    end
end
function H.lastResult(player)
    for i = #H.sent, 1, -1 do
        local s = H.sent[i]
        if s.command == "result" and (player == nil or s.to == player) then
            return s.args
        end
    end
    return nil
end
function H.clearSent() H.sent = {} end

-- ---------------------------------------------------------------- stats
CharacterStat = {}
for _, n in ipairs({"UNHAPPINESS", "BOREDOM", "STRESS", "PANIC", "ENDURANCE", "FATIGUE"}) do
    local max = (n == "STRESS" or n == "ENDURANCE" or n == "FATIGUE") and 1 or 100
    CharacterStat[n] = {getMaximumValue = function() return max end, getMinimumValue = function() return 0 end, name = n}
end
Perks = {LongBlade = {name = "LongBlade"}, Crossbow = {name = "Crossbow"}, Aiming = "Aiming"}
H.xp = {}
function addXpNoMultiplier(p, perk, n) table.insert(H.xp, {p = p, perk = perk, n = n}) end
function addXp(p, perk, n) table.insert(H.xp, {p = p, perk = perk, n = n}) end
function instanceof(o, cls) return type(o) == "table" and o.class == cls end
SyncPlayerStatsPacket = {getBitMaskForStat = function() return 4 end}
H.statSyncs = 0
function syncPlayerStats() H.statSyncs = H.statSyncs + 1 end

-- ---------------------------------------------------------------- items and inventories
local Item = {}
-- weapon stats per full type (Treasured Blades parity tests): getters read from here
H.weaponStats = {}
Item.__index = function(self, k)
    local f = rawget(Item, k)
    if f ~= nil then return f end
    local ws = H.weaponStats[rawget(self, "full")]
    if ws and ws[k] ~= nil then
        local v = ws[k]
        return function() return v end
    end
    return nil
end
H.nextId = 1
function H.newItem(full)
    local it = setmetatable({full = full, md = {}, id = H.nextId}, Item)
    H.nextId = H.nextId + 1
    return it
end
function Item:getFullType() return self.full end
function Item:getModData() return self.md end
function Item:getDisplayName() return self.full end
function Item:getContainer() return self.container end
function Item:getID() return self.id end
H.unknownTypes = {}
function instanceItem(full)
    if H.unknownTypes[full] then return nil end
    return H.newItem(full)
end

local Inv = {}
Inv.__index = Inv
function H.newInv() return setmetatable({items = {}}, Inv) end
function Inv:AddItem(it)
    if type(it) == "string" then   -- ItemContainer.AddItem(String fullType) makes the item
        it = H.newItem(it)
    end
    table.insert(self.items, it)
    it.container = self
    return it
end
function Inv:DoRemoveItem(it)
    for i, x in ipairs(self.items) do
        if x == it then
            table.remove(self.items, i)
            it.container = nil
            return
        end
    end
end
function Inv:count(full)
    local n = 0
    for _, x in ipairs(self.items) do
        if x.full == full then n = n + 1 end
        if x.inner then n = n + x.inner:count(full) end
    end
    return n
end
function Inv:getCountTypeRecurse(t)
    local n = 0
    for _, x in ipairs(self.items) do
        if x.full == t or x.full:sub(-(#t + 1)) == "." .. t then n = n + 1 end
        if x.inner then n = n + x.inner:getCountTypeRecurse(t) end
    end
    return n
end
function Inv:getItemWithIDRecursiv(id)
    for _, x in ipairs(self.items) do
        if x.id == id then return x end
        if x.inner then
            local y = x.inner:getItemWithIDRecursiv(id)
            if y then return y end
        end
    end
    return nil
end
function Inv:getFirstTypeRecurse(full)
    for _, x in ipairs(self.items) do
        if x.full == full then return x end
        if x.inner then
            local y = x.inner:getFirstTypeRecurse(full)
            if y then return y end
        end
    end
    return nil
end
-- java.util.ArrayList stand-in
local function jlist(t)
    return {size = function() return #t end, get = function(_, i) return t[i + 1] end}
end
H.jlist = jlist
function Inv:getAllTypeRecurse(full)
    local out = {}
    local function walk(inv)
        for _, x in ipairs(inv.items) do
            if x.full == full then table.insert(out, x) end
            if x.inner then walk(x.inner) end
        end
    end
    walk(self)
    return jlist(out)
end
H.adds, H.removes = 0, 0
H.modSyncs = 0
function syncItemModData() H.modSyncs = H.modSyncs + 1 end

-- Barangay Tales stand-in: since 0.4.0 Jamie's Crossbows must NEVER call it (BT hooks in instead)
H.btAwards = {}
function H.installBT(loaded)
    BT = {playerId = function(p) return string.lower(p:getUsername()) end}
    PersonalReputation = {award = function(pid, amount, source, sourceId)
        table.insert(H.btAwards, {pid = pid, amount = amount, source = source, sourceId = sourceId})
        return amount
    end}
    Persistence = {loaded = loaded ~= false}
end
function H.removeBT() BT, PersonalReputation, Persistence = nil, nil, nil end
function sendAddItemToContainer() H.adds = H.adds + 1 end
function sendRemoveItemFromContainer() H.removes = H.removes + 1 end

-- ---------------------------------------------------------------- players
local Player = {}
Player.__index = Player
function H.newPlayer(name, role, x, y, z)
    local stats = {v = {UNHAPPINESS = 0, BOREDOM = 0, STRESS = 0, PANIC = 0, ENDURANCE = 1, FATIGUE = 0}}
    function stats:get(s) return self.v[s.name] end
    function stats:remove(s, a) self.v[s.name] = math.max(0, self.v[s.name] - a) return true end
    function stats:add(s, a) self.v[s.name] = self.v[s.name] + a return true end
    function stats:set(s, a) self.v[s.name] = a return true end
    return setmetatable({name = name, role = role, x = x or 100.5, y = y or 100.5, z = z or 0, inv = H.newInv(), stats = stats, steam = 7656 + #name,
                         class = "IsoPlayer", worn = {}}, Player)
end
function Player:getPrimaryHandItem() return self.primary end
function Player:getForwardDirection()
    local d = self.dir or {1, 0}
    return {getX = function() return d[1] end, getY = function() return d[2] end}
end
function Player:getPerkLevel(p) return (self.perks or {})[p] or 0 end
function Player:getOnlineID() return #self.name end
function Player:setVariable(k, v) self.vars = self.vars or {}; self.vars[k] = v end
function Player:getVariableFloat(k, d) local v = (self.vars or {})[k]; if v == nil then return d end return v end
function Player:getSecondaryHandItem() return self.secondary end
function Player:getWornItems()
    local w = self.worn
    return {size = function() return #w end, get = function(_, i) local it = w[i + 1] return {getItem = function() return it end} end}
end
function Player:getUsername() return self.name end
function Player:getRole()
    if not self.role then return nil end
    local role = self.role
    return {getName = function() return role end, hasAdminPower = function() return role == "admin" end}
end
function Player:getAccessLevel() return self.role or "none" end
function Player:getX() return self.x end
function Player:getY() return self.y end
function Player:getZ() return self.z end
function Player:getInventory() return self.inv end
function Player:getStats() return self.stats end
function Player:isDead() return false end
function Player:getVehicle() return nil end
function Player:getSteamID() return self.steam end
function Player:setHaloNote() end

H.online = {}
local function jlist(t)
    return {size = function() return #t end, get = function(_, i) return t[i + 1] end}
end
function getOnlinePlayers() return jlist(H.online) end
function getSpecificPlayer(i) return H.online[i + 1] end

-- ---------------------------------------------------------------- world
H.squares = {}
local Square = {}
Square.__index = Square
local function key(x, y, z) return x .. "," .. y .. "," .. z end
function H.square(x, y, z, opts)
    opts = opts or {}
    local sq = setmetatable({x = x, y = y, z = z, objects = {}, world = {}, floor = opts.noFloor and nil or true,
                             room = opts.room, solid = opts.solid}, Square)
    H.squares[key(x, y, z)] = sq
    return sq
end
function Square:getX() return self.x end
function Square:getY() return self.y end
function Square:getZ() return self.z end
function Square:getFloor() return self.floor end
function Square:getObjects() return jlist(self.objects) end
function Square:getWorldObjects() return jlist(self.world) end
function Square:isSolid() return self.solid == true end
function Square:isSolidTrans() return false end
function Square:isFree() return self.solid ~= true end
function Square:getRoom() return self.room end
function Square:getCell() return H.cell end
function Square:AddWorldInventoryItem(full, fx, fy, fz)
    local it = H.newItem(full)
    table.insert(self.world, {getItem = function() return it end, item = it, fx = fx, fy = fy})
    return it
end
function Square:getMovingObjects() return jlist(self.moving or {}) end
function Square:isBlockedTo(other) return (self.blockedTo or {})[other] == true end
function Square:AddSpecialObject(o) table.insert(self.objects, o) o.square = self end
function Square:transmitRemoveItemFromSquare(o)
    for i, x in ipairs(self.objects) do
        if x == o then table.remove(self.objects, i) return 1 end
    end
    return 0
end
function Square:RemoveTileObject(o) return self:transmitRemoveItemFromSquare(o) end
function Square:RecalcProperties() end
function Square:RecalcAllWithNeighbours() end
function H.placeItem(sq, full)
    local it = H.newItem(full)
    local wo = {getItem = function() return it end}
    table.insert(sq.world, wo)
    return wo
end

H.cell = {}
function H.cell:getGridSquare(x, y, z) return H.squares[key(x, y, z)] end
function getCell() return H.cell end

local Obj = {}
Obj.__index = Obj
IsoObject = {}
function IsoObject.new(cell, sq, sprite)
    return setmetatable({sprite = sprite, md = {}, sq = sq}, Obj)
end
function Obj:setName(n) self.name = n end
function Obj:getName() return self.name end
function Obj:getModData() return self.md end
function Obj:getSprite() local s = self.sprite return {getName = function() return s end} end
function Obj:getSquare() return self.square or self.sq end
function Obj:transmitCompleteItemToClients() end
function Obj:transmitUpdatedSpriteToClients() end
function Obj:transmitModData() self.mdSent = (self.mdSent or 0) + 1 end

-- line of sight: walls are listed as blocked pairs of squares on a line (tests set them)
H.walls = {}
LosUtil = {}
function LosUtil.lineClear(cell, x0, y0, z0, x1, y1, z1, ignoreDoors)
    for _, w in ipairs(H.walls) do
        -- a wall is a vertical line x = w.x between y ranges; blocks if the segment crosses it
        if (x0 < w.x) ~= (x1 < w.x) and math.min(y0, y1) <= w.y1 and math.max(y0, y1) >= w.y0 then
            return w.door and "ClearThroughClosedDoor" or "Blocked"
        end
    end
    return "Clear"
end

-- safehouses
H.safehouses = {}
SafeHouse = {}
function SafeHouse.getSafeHouse(sq)
    for _, s in ipairs(H.safehouses) do
        if sq.x >= s.x0 and sq.x <= s.x1 and sq.y >= s.y0 and sq.y <= s.y1 then
            return {playerAllowed = function(_, p) return s.members[p:getUsername()] == true end}
        end
    end
    return nil
end

-- script manager (bag DoParam)
H.params = {}
H.paramGetter = {}   -- script property -> getter (filled by the blade tests)
ScriptManager = {instance = {getItem = function(_, full)
    return {DoParam = function(_, p)
                table.insert(H.params, full .. " " .. p)
                local k, v = string.match(p, "^(%w+) = (.+)$")
                local g = k and H.paramGetter[k]
                if g and H.weaponStats[full] then
                    H.weaponStats[full][g] = tonumber(v) or (v == "true" and true) or (v == "false" and false) or v
                end
            end,
            getNormalTexture = function() return {tex = "Item:" .. full} end}
end}}

-- loot tables
ProceduralDistributions = {list = {}}
function H.lootLists(names)
    ProceduralDistributions.list = {}
    for _, n in ipairs(names) do
        ProceduralDistributions.list[n] = {rolls = 1, items = {}}
    end
end

-- ---------------------------------------------------------------- Java strictness
-- The game's Java methods reject extra arguments, INCLUDING trailing nils
-- ("expected 0 arguments, got 2"). Make the stand-ins do the same, so a helper
-- that pads arguments fails here instead of in the game.
local function strict(tbl, allow, label)
    for name, fn in pairs(tbl) do
        if type(fn) == "function" and name ~= "__index" and not allow[name] then
            tbl[name] = function(self, ...)
                local n = select("#", ...)
                if n > 0 then
                    error((label or "") .. ":" .. name .. " expected 0 arguments, got " .. n)
                end
                return fn(self)
            end
        end
    end
end
H.strict = strict
strict(Square, {getMovingObjects = true, AddSpecialObject = true, transmitRemoveItemFromSquare = true, RemoveTileObject = true, isFree = true,
                AddWorldInventoryItem = true, isBlockedTo = true,
                RecalcAllWithNeighbours = true}, "Square")
strict(Player, {setHaloNote = true, getPerkLevel = true, setVariable = true, getVariableFloat = true}, "Player")
strict(Obj, {setName = true}, "IsoObject")
strict(Item, {}, "Item")
strict(Inv, {AddItem = true, DoRemoveItem = true, count = true, getFirstTypeRecurse = true, getItemWithIDRecursiv = true,
                  getAllTypeRecurse = true, getCountTypeRecurse = true}, "Inventory")
local rawRole = Player.getRole
Player.getRole = function(self, ...)
    if select("#", ...) > 0 then error("Player:getRole expected 0 arguments") end
    local r = rawRole(self)
    if r then strict(r, {}, "Role") end
    return r
end

function H.loadAll()
    H.mode = "server"
    require("JamiesCrossbows/JC_Core")
    require("JamiesCrossbows/JC_Catalog")
    require("JamiesCrossbows/JC_Net")
    require("JamiesCrossbows/JC_Reload")
    require("JamiesCrossbows/JC_Server")
end

return H
