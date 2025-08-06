from .base import TextCodec
from src.codecs.tables import GEN3_TABLE, REVERSE_TABLE
from typing import Union, List

class Gen3TextCodec(TextCodec):
    def decode(self, data: bytes) -> str:
        result, i = [], 0
        while i < len(data):
            b = data[i]
            if b == 0xFF:
                break
            elif b == 0xFB:
                result.append("\f")
            elif b == 0xFE:
                result.append("\n")
            elif b == 0xFC and i + 1 < len(data):
                code = data[i + 1]
                if code == 0x10:
                    result.append("{PLAYER}")
                elif code == 0x11:
                    result.append("{RIVAL}")
                elif code == 0x0C:
                    result.append("→")
                else:
                    result.append(f"[FC {code:02X}]")
                i += 1
            else:
                result.append(GEN3_TABLE.get(b, f"[{b:02X}]"))
            i += 1
        return "".join(result)

    def encode(self, text: str, max_len: int = 255) -> bytes:
        encoded = bytearray()
        i = 0
        while i < len(text):
            # Handle placeholders first
            if text.startswith("{PLAYER}", i):
                encoded.extend([0xFC, 0x10])
                i += len("{PLAYER}")
                continue
            if text.startswith("{RIVAL}", i):
                encoded.extend([0xFC, 0x11])
                i += len("{RIVAL}")
                continue

            c = text[i]
            code: Union[int, List[int], None] = REVERSE_TABLE.get(c)
            if isinstance(code, list):
                # extend by each byte
                encoded.extend(code)
            elif isinstance(code, int):
                encoded.append(code)
            else:
                # fallback for A–Z, a–z, or unknown
                if "A" <= c <= "Z":
                    encoded.append(0xBB + ord(c) - 65)
                elif "a" <= c <= "z":
                    encoded.append(0xD5 + ord(c) - 97)
                else:
                    encoded.append(0x50)
            i += 1
            if len(encoded) >= max_len - 1:
                break

        encoded.append(0xFF)
        return bytes(encoded)

