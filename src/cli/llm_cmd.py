# src/cli/llm_cmd.py
import logging
from src.cli.parser import parse_args
from src.cli.extract_cmd import run_extraction
from src.cli.ipc_cmd import run_ipc_loop
from src.llm.llama_client import LlamaClient
from src.llm.prompt_builder import PromptBuilder
from src.llm.dialogue_generator import DialogueGenerator
from src.codecs.gen3 import Gen3TextCodec

def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings, ipc_mode = parse_args()
    codec = Gen3TextCodec()

    llm_client = LlamaClient(settings.llm)
    prompt_builder = PromptBuilder(few_shot=settings.few_shot_examples)
    generator = DialogueGenerator(llm_client, settings.character, prompt_builder)

    if ipc_mode:
        run_ipc_loop(settings, generator, codec)
    else:
        original = "I came here with some friends to catch us some BUG POKéMON!\n"
        rewrite = ""
        while len(rewrite) <= 4:
            rewrite = generator.generate(original)
            logging.info(f"Generated text: {rewrite}")
        run_extraction(settings.extract)

