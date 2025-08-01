import argparse
from src.rom.dialog_extractor import DialogExtractor

DIALOG_START = 0x00172250 + 5  # Adjusted to real start
DIALOG_END = 0x1A4E26  # Exclusive end bound

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", default="gba_rom/fire_red.gba")
    parser.add_argument("--out", default="data/dialog_map.json")
    return parser.parse_args()

def main():
    print("--- FireRed Dialog Extractor ---")
    args = parse_args()
    extractor = DialogExtractor(args.rom)
    dialog_map = extractor.extract(DIALOG_START, DIALOG_END)
    extractor.save(dialog_map, args.out)
    print(f"Saved to {args.out}")

if __name__ == "__main__":
    main()

