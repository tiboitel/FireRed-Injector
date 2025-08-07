import argparse
from typing import Any
from pathlib import Path

def parse_args() -> Any:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path, default=Path("gba_rom/fire_red.gba"))
    parser.add_argument("--out", type=Path, default=Path("data/dialog_map.json"))
    parser.add_argument("--model", type=Path, required=True,
                        help="Path to your GGUF model file")
    parser.add_argument("--ipc", action="store_true",
                        help="Enable IPC mode with Lua")
    return parser.parse_args()

