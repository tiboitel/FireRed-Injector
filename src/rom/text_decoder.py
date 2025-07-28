GEN3_TABLE = {
    0x00: " ", 0xE0: ".", 0xE1: ",", 0xE5: "'", 0xE9: "é",
    0xEF: "!", 0xF0: "?", 0xF1: '"', 0xF2: "…", 0xF4: "♂", 0xF5: "♀",
    0xFE: "\n", 0xFB: "\f", 0xFF: ""  # terminator
}
for i in range(0xA1, 0xAB):  # digits 0–9
    GEN3_TABLE[i] = str(i - 0xA1)
for i in range(0xBB, 0xD5):  # A–Z
    GEN3_TABLE[i] = chr(65 + (i - 0xBB))
for i in range(0xD5, 0xEF):  # a–z
    GEN3_TABLE[i] = chr(97 + (i - 0xD5))

REVERSE_TABLE = {v: k for k, v in GEN3_TABLE.items()}

def decode_text(data: bytes) -> str:
    result = []
    for b in data:
        if b == 0xFF:  # terminator
            break
        result.append(GEN3_TABLE.get(b, "?"))
    return "".join(result)

def encode_text(text: str, max_len: int = 255) -> bytes:
    encoded = bytearray()
    for c in text:
        code = REVERSE_TABLE.get(c)
        if code is not None:
            encoded.append(code)
        elif "A" <= c <= "Z":
            encoded.append(0xBB + ord(c) - 65)
        elif "a" <= c <= "z":
            encoded.append(0xD5 + ord(c) - 97)
        else:
            encoded.append(0x50)  # fallback
        if len(encoded) >= max_len - 1:
            break
    encoded.append(0xFF)  # end marker
    return bytes(encoded)

