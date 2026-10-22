-- Jamie's Crossbows - shared basics: namespace, logging, sandbox options,
-- who counts as staff, small helpers.
--
-- Kahlua notes (B42.21): no next(), no string.rep(), no goto, no loadstring.
-- Nothing here calls game APIs at load time.

JamiesCrossbows = JamiesCrossbows or {}
local JC = JamiesCrossbows

JC.MODULE = "JamiesCrossbows"   -- item script module and network channel
JC.PREFIX = "[JamiesCrossbows] "

-- ---------------------------------------------------------------------------
-- logging
-- ---------------------------------------------------------------------------
function JC.log(msg)
    print(JC.PREFIX .. tostring(msg))
end

-- ---------------------------------------------------------------------------
-- helpers
-- ---------------------------------------------------------------------------
--- Calls obj:method(...) safely; nil on any error.
--- Passes EXACTLY the arguments given: the game's Java methods count trailing
--- nils as arguments ("expected 0 arguments, got 2"), so never pad them.
function JC.try(obj, method, ...)
    if obj == nil then
        return nil
    end
    local n = select("#", ...)
    local args = {...}
    local ok, res = pcall(function()
        local fn = obj[method]
        if not fn then
            return nil
        end
        if n == 0 then
            return fn(obj)
        end
        return fn(obj, unpack(args, 1, n))
    end)
    if ok then
        return res
    end
    return nil
end

--- Singleplayer (or a client-less host): both sides share one Lua state.
function JC.isLocal()
    local client = isClient and isClient() or false
    local server = isServer and isServer() or false
    return not client and not server
end

function JC.copy(t)
    if type(t) ~= "table" then
        return t
    end
    local r = {}
    for k, v in pairs(t) do
        r[k] = JC.copy(v)
    end
    return r
end

function JC.count(t)
    local n = 0
    if type(t) == "table" then
        for _ in pairs(t) do
            n = n + 1
        end
    end
    return n
end

function JC.clamp(v, lo, hi)
    if v < lo then
        return lo
    end
    if v > hi then
        return hi
    end
    return v
end

--- A finite number or nil (rejects NaN and infinities from the network).
function JC.num(v)
    v = tonumber(v)
    if v == nil or v ~= v or v == math.huge or v == -math.huge then
        return nil
    end
    return v
end

--- Random integer 1..n on whichever side runs this (server for rewards).
function JC.randomInt(n)
    if n <= 1 then
        return 1
    end
    if ZombRand then
        return ZombRand(n) + 1
    end
    return math.random(1, n)
end

--- Random float in [0, 1).
function JC.random01()
    if ZombRandFloat then
        local ok, r = pcall(ZombRandFloat, 0.0, 1.0)
        if ok and type(r) == "number" and r < 1 then
            return r
        end
    end
    return (JC.randomInt(1000000) - 1) / 1000000
end

function JC.username(player)
    local name = JC.try(player, "getUsername")
    return name and tostring(name) or "?"
end

function JC.nowText()
    local ok, t = pcall(function()
        return getTimestamp and getTimestamp() or 0
    end)
    return ok and tostring(t) or "0"
end

-- ---------------------------------------------------------------------------
-- sandbox options (page "Jamie's Crossbows", table SandboxVars.JamiesCrossbows)
-- Every read is validated: missing, wrong type or out of range -> default.
-- ---------------------------------------------------------------------------
local function rawOpt(name)
    local ok, v = pcall(function()
        return SandboxVars and SandboxVars.JamiesCrossbows and SandboxVars.JamiesCrossbows[name]
    end)
    if ok then
        return v
    end
    return nil
end

function JC.optNum(name, default, lo, hi)
    local v = JC.num(rawOpt(name))
    if v == nil then
        return default
    end
    if lo and v < lo then
        return lo
    end
    if hi and v > hi then
        return hi
    end
    return v
end

function JC.optBool(name, default)
    local v = rawOpt(name)
    if v == true or v == false then
        return v
    end
    return default
end

-- ---------------------------------------------------------------------------
-- staff (same rules as JamieCore.Admin, kept here so this mod stands alone).
-- Reads only the player object, never GameClient.connection (null on a
-- dedicated server). B42 roles first, then the older access level names.
-- ---------------------------------------------------------------------------
JC.RANK = {none = 0, observer = 1, gm = 2, overseer = 3, moderator = 4, admin = 5}

local function rankOf(name)
    if type(name) ~= "string" then
        return 0
    end
    return JC.RANK[string.lower(name)] or 0
end

local function me()
    local p
    pcall(function()
        p = getPlayer and getPlayer() or getSpecificPlayer(0)
    end)
    return p
end

function JC.rank(player)
    if JC.isLocal() then
        return JC.RANK.admin -- singleplayer: you are testing your own game
    end
    local best = 0
    local role = JC.try(player, "getRole")
    if role then
        best = math.max(best, rankOf(JC.try(role, "getName")))
        if best < JC.RANK.admin and JC.try(role, "hasAdminPower") == true then
            best = JC.RANK.admin
        end
    end
    best = math.max(best, rankOf(JC.try(player, "getAccessLevel")))
    return best
end

--- Allowed to use the admin tools? Sandbox StaffLevel: 1 = admins only (default),
--- 2 = admins and moderators.
function JC.isStaff(player)
    local need = JC.RANK.admin
    if JC.optNum("StaffLevel", 1, 1, 2) >= 2 then
        need = JC.RANK.moderator
    end
    return JC.rank(player) >= need
end

--- Client asking about itself (only decides what the menu shows; the server
--- checks again for real).
function JC.amIStaff()
    return JC.isStaff(me())
end

-- ---------------------------------------------------------------------------
-- the catalog (lua/shared/JamiesCrossbows/JC_Catalog.lua, generated)
-- ---------------------------------------------------------------------------
function JC.catalog()
    if not JC.Catalog then
        pcall(require, "JamiesCrossbows/JC_Catalog")
    end
    local Cat = JC.Catalog or {crossbows = {}}
    if not JC.byFull then
        JC.byFull, JC.byId = {}, {}
        for _, c in ipairs(Cat.crossbows or {}) do
            local full = (Cat.module or JC.MODULE) .. "." .. c.id
            local def = {id = c.id, key = c.key, name = c.name, full = full}
            JC.byFull[full] = def
            JC.byId[c.id] = def
        end
    end
    return Cat
end

--- Is this item one of Jamie's Crossbows?
function JC.isCrossbow(item)
    JC.catalog()
    local full = item and JC.try(item, "getFullType")
    return full ~= nil and JC.byFull[full] ~= nil
end

function JC.boltFull()
    local Cat = JC.catalog()
    return (Cat.module or JC.MODULE) .. "." .. (Cat.bolt or "JC_CrossbowBolt")
end

return JC
