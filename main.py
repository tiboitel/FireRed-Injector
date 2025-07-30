from src.rom.rom_loader import RomLoader
from src.rom.text_decoder import decode_text
import json

ROM_PATH = "gba_rom/fire_red.gba"
DIALOG_START = 0x00172250 + 5  # Adjusted to real start
DIALOG_END = 0x1A4E26  # Exclusive end bound

def main():
    print("--- FireRed Dialog Extractor ---")
    rom = RomLoader(ROM_PATH)

    dialog_map = {}
    offset = DIALOG_START

    while offset < DIALOG_END:
        text_bytes = rom.read_bytes(offset, 255)

        # Find where this string ends
        end_index = 0
        for i, byte in enumerate(text_bytes):
            if byte in (0xFB, 0xFF):  # page or end
                end_index = i + 1
                break

        if end_index == 0:
            offset += 1
            continue

        actual_bytes = text_bytes[:end_index]
        decoded = decode_text(actual_bytes).strip()

        if decoded:
            # Use the hex representation of the byte string as the key
            hex_key = actual_bytes.hex()
            dialog_map[hex_key] = decoded

        offset += end_index

    print(f"Extracted {len(dialog_map)} dialogs.")

    with open("data/dialog_map.json", "w", encoding="utf-8") as f:
        json.dump(dialog_map, f, indent=2, ensure_ascii=False)

    print("Saved to data/dialog_map.json")

if __name__ == "__main__":
    main()

