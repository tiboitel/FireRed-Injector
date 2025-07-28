from src.rom.rom_loader import RomLoader
from src.rom.text_decoder import decode_text, encode_text

def main():
    rom = RomLoader("gba_rom/fire_red.gba")
    table_base = 0x03526A8  # Hypothetical pointer table start (adjust for your version)
    pointer_index = 123     # Based on map/NPC dialogue index
    ptr_offset = table_base + pointer_index * 4

    text_ptr = rom.read_pointer(ptr_offset)
    text_bytes = rom.read_bytes(text_ptr, 128)
    dialog = decode_text(text_bytes)
    print("Dialog:", dialog)

if __name__ == "__main__":
    main()
