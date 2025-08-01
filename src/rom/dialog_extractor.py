import json
from .text_decoder import decode_text
from .rom_loader import RomLoader

class DialogExtractor:
    def __init__(self, rom_path: str):
        self.rom = RomLoader(rom_path)

    def extract(self, start: int, end: int) -> dict:
        dialog_map = {}
        offset = start

        while offset < end:
            text_bytes = self.rom.read_bytes(offset, 255)

            end_index = next((i + 1 for i, b in enumerate(text_bytes) if b in (0xFB, 0xFF)), 0)
            if end_index == 0:
                offset += 1
                continue

            actual_bytes = text_bytes[:end_index]
            decoded = decode_text(actual_bytes).strip()

            if decoded:
                hex_key = actual_bytes.hex()
                dialog_map[hex_key] = decoded

            offset += end_index

        return dialog_map

    def save(self, dialog_map: dict, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(dialog_map, f, indent=2, ensure_ascii=False)

