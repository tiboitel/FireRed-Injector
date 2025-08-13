# src/cli/parser.py
import argparse
from pathlib import Path
from typing import Any
from src.config.settings import load_settings

def parse_args() -> Any:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("config.toml"), help="Path to the config file")
    parser.add_argument("--rom", type=Path, help="Path to the ROM file")
    parser.add_argument("--out", type=Path, help="Path to the output file")
    parser.add_argument("--model", type=Path, help="Path to the LLM model file")
    parser.add_argument("--provider", type=str, help="LLM provider name (e.g., llama, dummy)")
    parser.add_argument("--ipc", action="store_true", help="Enable IPC mode with Lua")
    args = parser.parse_args()

    settings = load_settings(args.config)

    if args.rom:
        settings.extract.rom_path = args.rom
    if args.out:
        settings.extract.output_path = args.out
    if args.model:
        settings.llm.model_path = args.model
    if args.provider:
        settings.llm.provider = args.provider

    return settings, args.ipc
