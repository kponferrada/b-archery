-- Jamie's Crossbows - admin give menu (client).
--
-- Right-click the world: "Jamie's Crossbows (admin)" > each crossbow, and a bundle of
-- bolts. Shown only to staff (sandbox StaffLevel); the server checks again before it
-- gives anything (server/JC_Server.lua, command "give"). The answer shows as a halo note.

if isServer() and not isClient() then
    return
end

require "JamiesCrossbows/JC_Core"
require "JamiesCrossbows/JC_Net"

local JC = JamiesCrossbows
JC.Admin = JC.Admin or {}
local A = JC.Admin

function A.give(id)
    JC.Net.request("give", {id = id})
end

function A.fill(playerNum, context, worldobjects, test)
    if test or not JC.amIStaff() then
        return
    end
    local Cat = JC.catalog()
    local root = context:addOption(getText("IGUI_JC_Admin"), nil, nil)
    local sub = ISContextMenu:getNew(context)
    context:addSubMenu(root, sub)
    for _, c in ipairs(Cat.crossbows or {}) do
        sub:addOption(c.name, c.id, A.give)
    end
    sub:addOption(getText("IGUI_JC_Admin_Bolts", tostring(Cat.boltBundle or 10)), Cat.bolt, A.give)
end

function A.onResult(args)
    local p = getPlayer and getPlayer()
    if not p then
        return
    end
    local text
    if args.ok then
        text = getText("IGUI_JC_Given", tostring(args.count or 1) .. "x " .. tostring(getItemNameFromFullType and
            getItemNameFromFullType(tostring(args.name)) or args.name))
    else
        text = getText(tostring(args.key or "IGUI_JC_Failed"))
    end
    JC.try(p, "setHaloNote", text)
end

JC.Net.on("result", A.onResult)
if Events and Events.OnFillWorldObjectContextMenu then
    Events.OnFillWorldObjectContextMenu.Add(A.fill)
end

return A
