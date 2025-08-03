import logging
import argparse
import time
from pathlib import Path

from config import ExtractConfig, LlmConfig
from src.loaders.rom_loader import RomLoader
from src.codecs.gen3 import Gen3TextCodec
from src.extractors.dialog import DialogExtractor
from src.llm.llama_client import LlamaClient
from src.llm.dialogue_generator import DialogueGenerator
from src.llm.character_card import CharacterCard
from src.llm.prompt_builder import PromptBuilder
from src.utils.io import save_json

# === IPC Setup ===

IPC_DIR = Path("/home/tiboitel/Downloads/shared_ipc")
INPUT_FILE = IPC_DIR / "dialog_in.txt"
OUTPUT_FILE = IPC_DIR / "dialog_out.txt"

def wait_for_input(timeout=5.0) -> str | None:
    start = time.time()
    while time.time() - start < timeout:
        if INPUT_FILE.exists():
            content = INPUT_FILE.read_text(encoding="utf-8").strip()
            if content:
                return content
        time.sleep(0.1)
    return None

def write_output(text: str) -> None:
    OUTPUT_FILE.write_text(text.strip(), encoding="utf-8")

def clear_output_file() -> None:
    OUTPUT_FILE.write_text("", encoding="utf-8")

def _format_rewrite(s: str) -> str:
    s = list(s)
    i = 24
    toggle = True  # True for \n, False for \t
    while i < len(s):
        # Find next whitespace at or after index `i`
        j = next((j for j in range(i, len(s)) if s[j].isspace()), -1)
        if j == -1:
            break
        s[j] = '\n' if toggle else '\f'
        toggle = not toggle
        i = j + 24  # Continue checking after the last replaced character
    return ''.join(s)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--rom", type=Path, default=Path("gba_rom/fire_red.gba"))
    p.add_argument("--out", type=Path, default=Path("data/dialog_map.json"))
    p.add_argument("--model", type=Path, required=True,
                   help="Path to your GGUF model file")
    p.add_argument("--ipc", action="store_true",
                   help="Enable IPC mode with Lua")
    return p.parse_args()

def run_extraction(extract_cfg: ExtractConfig):
    loader = RomLoader(str(extract_cfg.rom_path))
    codec = Gen3TextCodec()
    extractor = DialogExtractor(loader, codec,
                                extract_cfg.start_offset,
                                extract_cfg.end_offset)
    raw_map = extractor.extract()
    save_json(raw_map, extract_cfg.output_path)
    logging.info(f"All dialogs saved to {extract_cfg.output_path}")

def run_ipc_loop(generator: DialogueGenerator):
    logging.info("🔁 IPC Mode Enabled — Waiting for input from Lua...")
    IPC_DIR.mkdir(exist_ok=True)
    clear_output_file()

    try:
        while True:
            original = wait_for_input(timeout=0.5)
            if original:
                logging.info(f"🧠 Received: {original!r}")
                rewrite = ""
                while len(rewrite.strip()) < 5:
                    rewrite = generator.generate(original)
                logging.info(f"✍️  Rewritten: {rewrite}")
                write_output(_format_rewrite(rewrite))
                # Clear input to avoid duplication
                INPUT_FILE.write_text("", encoding="utf-8")
                time.sleep(0.1)
    except KeyboardInterrupt:
        logging.info("🚪 IPC mode terminated by user.")

def main():
    logging.basicConfig(level=logging.INFO)
    args = parse_args()

    extract_cfg = ExtractConfig(
        rom_path=args.rom,
        output_path=args.out,
        start_offset=0x00172255,
        end_offset=0x1A4E26,
    )

    llm_cfg = LlmConfig(model_path=args.model)

    character = CharacterCard(
        name="Bug Catcher Timmy",
        age=14,
        location="Viridian Forest Entrance",
        traits=["friendly", "energetic", "helpful"],
        motivation="Capture BUG POKéMON. Share hints. Get new friends.",
    )

    prompt_builder = PromptBuilder(few_shot="""
        Example:
        Original: “Gotta catch ’em all!”\nRewrite: “My net’s ready — bugs, show your might!”\n
        Original: “I’ll battle any Trainer!” → Rewrite: “Challengers, step up — Bug mastery awaits!”\n
    """)

    llm_client = LlamaClient(llm_cfg)
    generator = DialogueGenerator(llm_client, character, prompt_builder)

    if args.ipc:
        run_ipc_loop(generator)
    else:
        original = "I came here with some friends to catch us some BUG POKéMON!\n"
        rewrite = ""
        while len(rewrite) <= 4:
            rewrite = generator.generate(original)
            logging.info(f"Generated text: {rewrite}")
            run_extraction(extract_cfg)

if __name__ == "__main__":
    main()

