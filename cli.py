import logging
import argparse
from pathlib import Path

from config import ExtractConfig, LlmConfig
from src.loaders.rom_loader import RomLoader
from src.codecs.gen3 import Gen3TextCodec
from src.extractors.dialog import DialogExtractor
from src.llm.llama_client import LlamaClient
from src.llm.base import LlmClient
from src.llm.dialogue_generator import DialogueGenerator
from src.llm.character_card import CharacterCard
from src.llm.prompt_builder import PromptBuilder


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--rom", type=Path, default=Path("gba_rom/fire_red.gba"))
    p.add_argument("--out", type=Path, default=Path("data/dialog_map.json"))
    p.add_argument("--model", type=Path, required=True,
                   help="Path to your GGUF model file")
    return p.parse_args()

def main():
    logging.basicConfig(level=logging.INFO)
    args = parse_args()

    extract_cfg = ExtractConfig(
        rom_path=args.rom,
        output_path=args.out,
        start_offset=0x00172250 + 5,
        end_offset=0x1A4E26,
    )

    llm_cfg = LlmConfig(model_path=args.model)

    loader = RomLoader(str(extract_cfg.rom_path))
    codec = Gen3TextCodec()
    extractor = DialogExtractor(loader, codec,
                                extract_cfg.start_offset,
                                extract_cfg.end_offset)
    llm_client = LlamaClient(llm_cfg)
    character =  CharacterCard(
        name="Bug Catcher Timmy",
        age=10,
        location="Viridian Forest Entrance",
        traits=["enthusiastic", "naive", "excitable"],
        motivation="prove Bug-types are the best"
    )
    prompt_builder = PromptBuilder(few_shot="""
        Example:
        Input: “Gotta catch ’em all!” → Output: “My net’s ready — bugs, show your might!”
        Input: “I’ll battle any Trainer!” → Output:“Challengers, step up — Bug mastery awaits!”
        """
    )
    generator = DialogueGenerator(llm_client, character, prompt_builder)
    original = "You can't escape my bug army!"
    logging.info(f"Generated text: {generator.generate(original)}")
    raw_map = extractor.extract()
    extractor.save(raw_map, extract_cfg.output_path)
    logging.info(f"All dialogs saved to {extract_cfg.output_path}")

if __name__ == "__main__":
    main()

