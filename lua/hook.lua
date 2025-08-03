-- read_true_msgbox_string.lua
-- mGBA 0.10.5 – Dump the unknown "msgbox string" region

local SCRIPT_ENGINE_RAM = 0x03000EB0   -- 0 = game running, 1 = dialog active
local TARGET_ADDR      = 0x02021D18   -- "String to be displayed in a message box"
local MAX_LEN          = 255          -- reasonable cap
local lastState        = 0
local framesElapsed = 0

local PUNCT = {
	[0xAD] = ".", [0xB8] = ",", [0xAB] = "!", [0xAC] = "?",
	[0xB3] = '"', [0xB0] = "…", [0xFE] = "\n", [0xFB] = "\f",
	[0xFF] = ""
}

local function read8(a) return emu:read8(a) end

local tbl = {
	[0x00] = " ", [0x15] = "ß", [0x1B] = "é",
	[0xA1] = "0", [0xA2] = "1", [0xA3] = "2",
	[0xA4] = "3", [0xA5] = "4", [0xA6] = "5",
	[0xA7] = "6", [0xA8] = "7", [0xA9] = "8",
	[0xAA] = "9", [0xAB] = "!", [0xAE] = "-",
	[0xAF] = "…", [0xB8] = ",", [0xBA] = "/",
	[0xF0] = ":", [0xF1] = "Ä", [0xF2] = "Ö",
	[0xF3] = "Ü", [0xF4] = "♂", [0xF5] = "♀",
}

local function code_to_ascii(b)
	if b >= 0xBB and b <= 0xD4 then
		return string.char(65 + (b - 0xBB))
	elseif b >= 0xD5 and b <= 0xEE then
		return string.char(97 + (b - 0xD5))
	elseif tbl[b] then
		return tbl[b]
	elseif b == 0x50 or b == 0xFF then
		return ""
	else
		return "?"
	end
end

local ascii_to_code_map = {
  [" "] = 0x00, ["!"] = 0xAB, ["'"] = 0xE5, [","] = 0xB4,
  ["-"] = 0xAE, ["."] = 0xAD, ["/"] = 0xBA, [":"] = 0xF0,
  ["?"] = 0xAC, ["…"] = 0xAF, ["é"] = 0x1B, ["ß"] = 0x15,
  ["♂"] = 0xF4, ["♀"] = 0xF5, ["\n"] = 0xFE, ["\f"] = 0xFB,
  ["0"] = 0xA1, ["1"] = 0xA2, ["2"] = 0xA3, ["3"] = 0xA4,
  ["4"] = 0xA5, ["5"] = 0xA6, ["6"] = 0xA7, ["7"] = 0xA8,
  ["8"] = 0xA9, ["9"] = 0xAA, ['"']= 0xB3
}

local function ascii_to_code(c)
  local b = ascii_to_code_map[c]
  if b then return b end

  local byte = string.byte(c)
  if byte >= 65 and byte <= 90 then -- A-Z
    return 0xBB + (byte - 65)
  elseif byte >= 97 and byte <= 122 then -- a-z
    return 0xD5 + (byte - 97)
  end

  return 0x50 -- fallback: terminator / unknown char
end

function sleep(n)
  os.execute("sleep " .. tonumber(n))
end

function writeDialogInput(text)
  local f = io.open("shared_ipc/dialog_in.txt", "w")
  if f then
    f:write(text)
    f:close()
  else
    console:log("❌ Failed to write input dialog")
  end
end

function readDialogOutput()
  local f = io.open("shared_ipc/dialog_out.txt", "r")
  if not f then return nil end

  local content = f:read("*a")
  f:close()
  if content == nil or content == "" then
    return nil
  end

  -- Clear previous LLM response
  -- local out = io.open("shared_ipc/dialog_out.txt", "w")
  -- if out then out:close() end

  return content
end

local function clearDialogBuffer()
	for i = 0, 127 do -- consrvative full clear
		emu:write8(0x02021D18 + i, 0xFF)
	end
end

local function writeDialogMessage(str)
	local base = 0x02021D18
	clearDialogBuffer()

	if str == nil then
		return
	end

	for i = 0, #str - 1 do
		local c = str:sub(i + 1, i + 1)
		local b = ascii_to_code(c)
		emu:write8(base + i, b)
	end
	emu:write8(base + #str, 0xFF) -- terminator
end

local function readDynamicString(addr, maxLen)
	local chars = {}
	for i = 0, maxLen - 1 do
		local b = read8(addr + i)
		if b == 0x50 or b == 0xFF then break end
		table.insert(chars, code_to_ascii(b))
	end
	return table.concat(chars)
end



local function onFrame()
	local cur = read8(SCRIPT_ENGINE_RAM)
	local msg = ""

	if cur == 1 and lastState == 1 then
		framesElapsed = framesElapsed + 1
	end
	if cur == 1 and framesElapsed >= 0 then
		local s = readDynamicString(TARGET_ADDR, MAX_LEN)
		writeDialogInput(s)	
		msg = readDialogOutput()
		if msg ~= nil and#msg > 0 and s ~= msg then
			writeDialogMessage(msg)
		end
		
	end
	if cur == 0 and lastState == 1 then
		clearDialogBuffer()
		framesElapsed = 0
	end
	lastState = cur
end

callbacks:add("frame", onFrame)

