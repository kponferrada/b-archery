-- Jamie's Crossbows - client/server messages on one channel ("JamiesCrossbows").
--
-- The client only ASKS. Every handler on the server re-checks who is asking,
-- what they asked for and whether it is allowed; nothing the client says about
-- rarity, value, admin status, water or position is trusted.
--
-- Singleplayer: the message is handed straight to the other side (a copy),
-- so the same code runs in SP, on a hosted game and on a dedicated server.
-- Same design as JamieCore.Net, kept here so this mod stands alone.

require "JamiesCrossbows/JC_Core"

local JC = JamiesCrossbows
JC.Net = JC.Net or {serverHandlers = {}, clientHandlers = {}, last = {}}
local N = JC.Net

--- Server: register a command. opts.staff = true refuses non-staff (logged);
--- opts.everyMs = per-player minimum gap between two calls (extra calls dropped).
function N.handle(command, fn, opts)
    N.serverHandlers[command] = {fn = fn, opts = opts or {}}
end

function N.on(command, fn)
    N.clientHandlers[command] = fn
end

local function nowMs()
    local ok, t = pcall(function()
        return getTimestampMs()
    end)
    return ok and t or 0
end

function N.dispatchServer(player, command, args)
    local h = N.serverHandlers[command]
    if not h then
        JC.log("Unknown command '" .. tostring(command) .. "' from " .. JC.username(player))
        return
    end
    if type(args) ~= "table" then
        args = {}
    end
    local who = JC.username(player)
    if h.opts.staff and not JC.isStaff(player) then
        JC.log("REFUSED staff command '" .. tostring(command) .. "' from " .. who .. " (not staff)")
        N.send(player, "result", {ok = false, key = "IGUI_JC_NotStaff"})
        return
    end
    local gap = h.opts.everyMs or 250
    local key = who .. "|" .. tostring(command)
    local t = nowMs()
    if N.last[key] and t - N.last[key] < gap then
        return -- too fast: dropped silently (double clicks, spam)
    end
    N.last[key] = t
    local ok, err = pcall(h.fn, player, args)
    if not ok then
        JC.log("Error in '" .. tostring(command) .. "' from " .. who .. ": " .. tostring(err))
        N.send(player, "result", {ok = false, key = "IGUI_JC_Failed"})
    end
end

function N.dispatchClient(command, args)
    local fn = N.clientHandlers[command]
    if not fn then
        return
    end
    local ok, err = pcall(fn, type(args) == "table" and args or {})
    if not ok then
        JC.log("Client error in '" .. tostring(command) .. "': " .. tostring(err))
    end
end

function N.send(player, command, args)
    args = args or {}
    if JC.isLocal() then
        N.dispatchClient(command, JC.copy(args))
        return
    end
    if player then
        pcall(sendServerCommand, player, JC.MODULE, command, args)
    end
end

function N.broadcast(command, args)
    args = args or {}
    if JC.isLocal() then
        N.dispatchClient(command, JC.copy(args))
        return
    end
    pcall(sendServerCommand, JC.MODULE, command, args)
end

function N.request(command, args)
    args = args or {}
    if JC.isLocal() then
        local p
        pcall(function()
            p = getPlayer and getPlayer() or getSpecificPlayer(0)
        end)
        N.dispatchServer(p, command, JC.copy(args))
        return
    end
    pcall(sendClientCommand, JC.MODULE, command, args)
end

local function onClientCommand(module, command, player, args)
    if module == JC.MODULE then
        N.dispatchServer(player, command, args)
    end
end

local function onServerCommand(module, command, args)
    if module == JC.MODULE then
        N.dispatchClient(command, args)
    end
end

if Events and not N.hooked then
    N.hooked = true
    if Events.OnClientCommand then
        Events.OnClientCommand.Add(onClientCommand)
    end
    if Events.OnServerCommand then
        Events.OnServerCommand.Add(onServerCommand)
    end
end

return N
