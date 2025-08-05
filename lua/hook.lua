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
  [0x1B] = byte(0x1B),
  [0xAB] = "!",
  [0xAC] = "?",
  [0xAE] = "-",
  [0xAF] = "･",
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
  -- clear buffer
  for i = 0, MAX_LEN - 1 do
    emu:write8(TARGET_ADDR + i, 0xFF)
  end 
  if not str or #str == 0 then
    return
  end
  str = str:gsub("’", "'") 
  local ptr = TARGET_ADDR
  local i = 1
  while i <= #str and (ptr - TARGET_ADDR) < (MAX_LEN - 1) do
    -- handle UTF-8 “é” (0xC3 0xA9) as one character
    local b1 = string.byte(str, i, i)
    local b2 = string.byte(str, i+1, i+1)
    if b1 == 0xC3 and b2 == 0xA9 then
      emu:write8(ptr, 0x1B)
      ptr = ptr + 1
      i = i + 2
    else
      local c = str:sub(i, i)
      local code = REVERSE_TABLE[c]
      if code then
        emu:write8(ptr, code)
      else
        -- fallback for A–Z, a–z
        local byteVal = string.byte(c)
        if byteVal and byteVal >= 65 and byteVal <= 90 then
          emu:write8(ptr, 0xBB + (byteVal - 65))
        elseif byteVal and byteVal >= 97 and byteVal <= 122 then
          emu:write8(ptr, 0xD5 + (byteVal - 97))
        else
          -- unknown; write terminator/filler
          emu:write8(ptr, 0x50)
        end
      end
      ptr = ptr + 1
      i = i + 1
    end
  end
  -- terminator
  emu:write8(ptr, 0xFF)
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
    console:log("Failed to write input dialog")
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

  local f = io.open("shared_ipc/dialog_out.txt", "w")
  if f then
    f:write("")
    f:close()
  end

  return content
end

local function clearDialogBuffer()
	for i = 0, 127 do -- consrvative full clear
		emu:write8(0x02021D18 + i, 0xFF)
	end
end

local msg = ""
local dialogueHooked = false
local readMessage = false
local writeMessage = false
original = nil

local function onFrame()
  local cur = read8(SCRIPT_ENGINE_RAM)
  if cur == 1 and lastState == 0 then
    framesElapsed = 0
    msg = ""
    original = nil
    dialogueHooked = false
    readMessage = false
    writeMessage = false
  end

  if cur == 1 and framesElapsed <= 2 then
    original = readDynamicString(TARGET_ADDR, MAX_LEN)
    if original ~= nil and #original >= 1 and dialogueHooked == false then
      original = original:gsub("'", "’")
      --- Sleept time estimation: ~number of tokens (len / 4) * generation per token.
      local sleep_time = #original * (#original / 2) / 1000
      if original ~= msg and writeMessage == false then
        writeDialogInput(original)
        sleep(sleep_time)
        writeMessage = true
        if readMessage == false then
          msg = readDialogOutput()
          readMessage = true
        end
      end
      original = nil
      dialogueHooked = true
    end
  end

  if cur == 1 then
    framesElapsed = framesElapsed + 1
 end

 if cur == 1 and framesElapsed >= 2 then
    if msg and msg ~= original then
      writeDialogMessage(msg)
    end
 end

  if cur == 0 and lastState == 1 then
    framesElapsed = 0
    clearDialogBuffer()
    readMessage = false
  end

 lastState = cur
end

callbacks:add("frame", onFrame)
