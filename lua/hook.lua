-- hook.lua — encoding & decoding aligned with Gen3TextCodec

local SCRIPT_ENGINE_RAM = 0x03000EB0
local TARGET_ADDR      = 0x02021D18
local MAX_LEN          = 255
local lastState, framesElapsed = 0, 0

local function byte(chr) return string.char(chr) end

-- Build GEN3_TABLE and REVERSE_TABLE just like Python
local GEN3_TABLE = {
  [0x00] = " ",
  [0xAD] = ".",
  [0xB8] = ",",
  [0xB4] = "'",  
  [0x1B] = byte(0x1B),
  [0xAB] = "!",
  [0xAC] = "?",
  [0xAE] = "-",
  [0xAF] = "･",
  [0xB3] = '"',
  [0xB0] = "…",
  [0xB1] = "“",
  [0xB2] = "”",
  [0xB3] = "‘",
  [0xB4] = "'",
  [0xB5] = "♂",
  [0xB6] = "♀",
  [0x0C] = "\t",
  [0xFE] = "\n",
  [0xFB] = "\f",
  [0xFF] = ""
}

-- A–Z
for b = 0xBB, 0xD4 do
  GEN3_TABLE[b] = string.char(65 + (b - 0xBB))
end
-- a–z
for b = 0xD5, 0xEE do
  GEN3_TABLE[b] = string.char(97 + (b - 0xD5))
end
-- digits 0–9 at 0xA1–0xAA
for b = 0xA1, 0xAA do
  GEN3_TABLE[b] = tostring(b - 0xA1)
end

-- REVERSE_TABLE maps characters to codes (or two‑byte sequences for placeholders)
local REVERSE_TABLE = {}
for byte, ch in pairs(GEN3_TABLE) do
  if ch ~= "" then
    REVERSE_TABLE[ch] = byte
  end
end
-- add control escapes
REVERSE_TABLE["\n"] = 0xFE
REVERSE_TABLE["\f"] = 0xFB
REVERSE_TABLE["\t"] = 0x0C
REVERSE_TABLE["{PLAYER}"] = {0xFC, 0x10}
REVERSE_TABLE["{RIVAL}"]  = {0xFC, 0x11}

-- helper functions
local function read8(addr) return emu:read8(addr) end

local function code_to_ascii(b)
  local ch = GEN3_TABLE[b]
  if ch then return ch end
  return "?"
end

local function ascii_to_code(c)
  local r = REVERSE_TABLE[c]
  if r then return r end

  local byte = string.byte(c)
  if byte >= 65 and byte <= 90 then
    return 0xBB + (byte - 65)
  elseif byte >= 97 and byte <= 122 then
    return 0xD5 + (byte - 97)
  end
  local f = string.format("%02x", byte)
  console:log("Unknown Byte in Encoding TABLE:")
  console:log(tostring(byte))
  console:log(f)
  return 0x50
end

-- Decode bytes at [addr, addr+maxLen)
local function readDynamicString(addr, maxLen)
  local result = {}
  for i = 0, maxLen - 1 do
    local b = read8(addr + i)
    if b == 0x50 or b == 0xFF then break end
    table.insert(result, code_to_ascii(b))
  end
  return table.concat(result)
end

-- Write text (Unicode-compatible) into dialog buffer
local function writeDialogMessage(str)
  local base = TARGET_ADDR
  -- clear with 0xFF bytes
  for i = 0, MAX_LEN - 1 do emu:write8(base + i, 0xFF) end
  if not str then return end

  local i = 1
  while i <= #str do
    -- check for placeholders first
    local sub = str:sub(i, i + 7)
    if sub == "{PLAYER}" then
      emu:write8(base, 0xFC); emu:write8(base + 1, 0x10); base = base + 2
      i = i + 8
    else
      sub = str:sub(i, i + 6)
      if sub == "{RIVAL}" then
        emu:write8(base, 0xFC); emu:write8(base + 1, 0x11); base = base + 2
        i = i + 7
      else
        local b = ascii_to_code(str:sub(i, i))
        emu:write8(base, b); base = base + 1; i = i + 1
      end
    end
    if base >= TARGET_ADDR + MAX_LEN - 1 then break end
  end
  emu:write8(base, 0xFF)
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

local msg = ""
original = nil

local function onFrame()
  local cur = read8(SCRIPT_ENGINE_RAM)
  if cur == 1 and lastState == 0 then
    framesElapsed = 0
    msg = ""
    original = nil
  end

  if cur == 1 and framesElapsed <= 2 then
    original = readDynamicString(TARGET_ADDR, MAX_LEN)
    if original ~= nil then
      writeDialogInput(original)
      original = nil
    end
  end

  if cur == 1 then
    framesElapsed = framesElapsed + 1
 end

 if cur == 1 and framesElapsed > 1 then
    --- msg = readDialogOutput()
    msg = "Hey, {PLAYER}! I’ve been waiting for\n you in Route 1…\f" ..
    "Your level 5 Pikachu’s looking strong—are\n you ready to catch ’em all?\f" ..
    "Let’s go, {RIVAL}! élan is everything. 12345\f"
    console:log("[INFO] ipc read :")
    console:log(msg)

   if msg and msg ~= original and framesElapsed >= 2 then
      writeDialogMessage(msg)
    end
 end

  if cur == 0 and lastState == 1 then
    clearDialogBuffer()
  end

 lastState = cur
end

callbacks:add("frame", onFrame)
