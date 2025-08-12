-- hook.lua — faithful rework of original timing + req_id IPC
-- Lua sends raw dialog bytes to Python, waits for encoded response,
-- injects response at the exact same moment as original PoC.
-- Cleans up IPC files after use. Uses small helper functions for clarity.

local SCRIPT_ENGINE_RAM = 0x03000EB0
local TARGET_ADDR      = 0x02021D18
local MAX_LEN          = 255
local GEN_TERM        = 0xFF
local FALLBACK_TERM   = 0x50

-- Timeouts / waits (seconds)
local POLL_SLEEP_SEC   = 0.1
local RESPONSE_TIMEOUT = 15.0

local lastState = 0
local framesElapsed = 0

local dialogueHooked = false
local requested = false
local msg_bytes = nil
local original_bytes = nil

-- small utilities ----------------------------------------------------------

local function read8(addr) return emu:read8(addr) end

-- Read raw Gen3 bytes from dialog buffer (stops at 0xFF or 0x50)
local function readRawDialog(addr, maxLen)
  local parts = {}
  for i = 0, maxLen - 1 do
    local b = read8(addr + i)
    if b == GEN_TERM then
      break
    end
    table.insert(parts, string.char(b))
  end
  return table.concat(parts)
end

local function write_binary_file(path, data)
  local f = io.open(path, "wb")
  if not f then
    console:log("IPC write error:", path)
    return false
  end
  f:write(data)
  f:close()
  return true
end

local function read_binary_file(path)
  local f = io.open(path, "rb")
  if not f then return nil end
  local d = f:read("*a")
  f:close()
  return d
end

local function safe_remove(path)
  -- ignore errors
  if path == nil then return end
  local ok, err = pcall(os.remove, path)
  if not ok and err then
    -- best-effort logging, continue
    console:log("IPC remove failed:", tostring(path), tostring(err))
  end
end

local function gen_req_id()
  return tostring(os.time()) .. "_" .. tostring(math.random(1, 1e6))
end

-- IPC helpers --------------------------------------------------------------
-- atomic write for requests using generic ipc_in_ naming
local function write_request(req_id, raw_bytes)
  local dir = "shared_ipc"
  local tmp_path = string.format("%s/ipc_in_%s.tmp", dir, req_id)
  local final_path = string.format("%s/ipc_in_%s.bin", dir, req_id)
  local f = io.open(tmp_path, "wb")
  if not f then
    console:log("IPC write error (tmp):", tmp_path)
    return false
  end
  f:write(raw_bytes)
  f:close()
  local ok, err = os.rename(tmp_path, final_path)
  if not ok then
    pcall(os.remove, tmp_path)
    console:log("IPC rename failed:", tostring(err))
    return false
  end
  return true
end


local function read_response(req_id)
  local dir = "shared_ipc"
  local path = string.format("%s/ipc_out_%s.bin", dir, req_id)
  return read_binary_file(path)
end

-- Memory write -------------------------------------------------------------

local function clearDialogBuffer()
  for i = 0, 127 do
    emu:write8(TARGET_ADDR + i, 0xFF)
  end
end

local function writeDialogBytesFromString(data)
  -- clear buffer first
  for i = 0, MAX_LEN - 1 do
    emu:write8(TARGET_ADDR + i, 0xFF)
  end
  for i = 1, #data do
    emu:write8(TARGET_ADDR + i - 1, string.byte(data, i))
  end
end

-- Main frame handler (preserves original PoC behavior) --------------------

local function onFrame()
  local cur = read8(SCRIPT_ENGINE_RAM)

  -- dialog box just opened -> reset
  if cur == 1 and lastState == 0 then
    framesElapsed = 0
    dialogueHooked = false
    requested = false
    msg_bytes = nil
    original_bytes = nil
  end

  -- While dialog open, within the first two frames read buffer & start IPC once
  if cur == 1 and framesElapsed <= 2 and not dialogueHooked then
    -- read the raw buffer exactly like original did
    console:log("[INFO] ReadRawDialog called.")
    local raw = readRawDialog(TARGET_ADDR, MAX_LEN)
    console:log(raw)
    if raw and #raw >= 3 and not requested then
      -- normalize quotes to match earlier behavior (if desired)
      -- raw = raw:gsub("'", "’") -- raw is binary; avoid changing bytes here
      original_bytes = raw
      local req_id = gen_req_id()
      console:log("[INFO] write_request called.")
      local ok = write_request(req_id, original_bytes)
      if not ok then
        console:log("Failed to write IPC request", req_id)
        dialogueHooked = true
      else
        requested = true
        -- Wait synchronously for Python response (like original sleep-based behavior).
        -- We poll response file with small sleeps until available or timeout.
        local start_time = os.time()
        local resp = nil
        while true do
          resp = read_response(req_id)
          if resp and #resp > 0 then
            -- cleanup request file and response file (response file removed by read_response reader? we remove explicitly)
            --
            console:log("[INFO] Readed response.")
            safe_remove(string.format("shared_ipc/ipc_in_%s.bin", req_id))
            safe_remove(string.format("shared_ipc/ipc_out_%s.bin", req_id))
            msg_bytes = resp
            break
          end
          -- timeout check (use os.time for seconds granularity)
          if os.difftime(os.time(), start_time) >= RESPONSE_TIMEOUT then
            console:log("[Error] IPC timeout for")
            console:log(req_id)
            -- cleanup request file
            safe_remove(string.format("shared_ipc/dialog_in_%s.bin", req_id))
            msg_bytes = nil
            break
          end
          -- small sleep to avoid busy-loop; relies on host shell sleep supporting fractional secs
          -- This mirrors original PoC behavior of blocking until LLM returns.
          os.execute("sleep " .. tostring(POLL_SLEEP_SEC))
        end
        dialogueHooked = true
      end
    end
  end

  -- advance frame counter while dialog box is open
  if cur == 1 then
    framesElapsed = framesElapsed + 1
  end

  -- On/after frame 2 (same as original) inject the message (if any)
  if cur == 1 and framesElapsed >= 2 then
    if msg_bytes and #msg_bytes > 0 then
      console:log("[INFO] Injected response.")
      writeDialogBytesFromString(msg_bytes)
      -- ensure we don't reinject
      msg_bytes = nil
    end
  end

  -- dialog closed -> reset and clear buffer like original
  if cur == 0 and lastState == 1 then
    framesElapsed = 0
    clearDialogBuffer()
    dialogueHooked = false
    requested = false
    msg_bytes = nil
    original_bytes = nil
  end

  lastState = cur
end

callbacks:add("frame", onFrame)

