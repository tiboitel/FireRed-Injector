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
from src.utils.format import format_dialogue
from src.ipc.file_ipc import init_ipc, read_request, write_response

# === IPC Setup ===

IPC_DIR = Path("/home/tiboitel/Downloads/shared_ipc")
INPUT_FILE = IPC_DIR / "dialog_in.txt"
OUTPUT_FILE = IPC_DIR / "dialog_out.txt"

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

from src.ipc.file_ipc import init_ipc, read_request, write_response

def run_ipc_loop(generator: DialogueGenerator, codec: Gen3TextCodec):
    logging.info("🔁 IPC Mode Enabled — Atomic IPC handshake")
    init_ipc()
    try:
        while True:
            req = read_request()
            if req:
                req_id, original = req
                logging.info(f"{original}")
                original = codec.decode(original)
                original = original.replace("\n", " ")
                original = original.replace("\x0c", " ")
                logging.info(f"[{req_id}] Received: {original!r}")

                rewrite = ""
                while len(rewrite.strip()) < 5:
                    rewrite = generator.generate(original)
                logging.info(f"[{req_id}] Rewritten: {rewrite!r}")
                rewrite = format_dialogue(rewrite)
                data = codec.encode(rewrite, max_len=255)
                write_response(req_id, data)

            time.sleep(0.05)
    except KeyboardInterrupt:
        logging.info("🚪 IPC mode terminated by user.")

def main():
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    codec = Gen3TextCodec()

    extract_cfg = ExtractConfig(
        rom_path=args.rom,
        output_path=args.out,
        start_offset=0x00172255,
        end_offset=0x1A4E26,
    )

    llm_cfg = LlmConfig(model_path=args.model)

    character = CharacterCard(
        name="The Great Uknown",
        age=27,
        location="All over the world",
        traits=[
            "belligerent", "abrupt", "fragile", "angry",
            "gritty", "dumb", "blunt", "gross", "south park fan",
            "emotionally unstable", "missguiding", "heavy dark-humor", "funny"
        ],
        motivation=(
            "Catch POKéMON by any means necessary—bribery or bruteforce. ",
            "Alienate friends with brutal honesty. Chase power, not happiness.",
            "Only give bad advices to other to lead them to wrong path.",
            "Really like to spend rumors.",
            "Gritty, sharp and funky humor"
        ),
    )

    prompt_builder = PromptBuilder(few_shot="""
        Example:
        Original: Gotta catch ’em all!\nRewrite: Let's get all these fuckers !\n
        Original: I’ll battle any Trainer! → Rewrite: “I can beat to dust any kids.\n
        Original: I love my POKéMON! → Rewrite: I love Digimons, yes I'm a psycho, dawg !!!\n
        Original: Hey ! I grow by beard since two years → Yo, wanna touch my sphagetti beard ? Mmh.. *insistant glare*
    """)

    llm_client = LlamaClient(llm_cfg)
    generator = DialogueGenerator(llm_client, character, prompt_builder)

    if args.ipc:
        run_ipc_loop(generator, codec)
    else:
        original = "I came here with some friends to catch us some BUG POKéMON!\n"
        rewrite = ""
        while len(rewrite) <= 4:
            rewrite = generator.generate(original)
            logging.info(f"Generated text: {rewrite}")
            run_extraction(extract_cfg)

if __name__ == "__main__":
    main()

