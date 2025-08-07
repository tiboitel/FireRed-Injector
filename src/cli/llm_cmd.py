import logging
from config import ExtractConfig, LlmConfig
from src.cli.parser import parse_args
from src.cli.extract_cmd import run_extraction
from src.cli.ipc_cmd import run_ipc_loop
from src.llm.llama_client import LlamaClient
from src.llm.character_card import CharacterCard
from src.llm.prompt_builder import PromptBuilder
from src.llm.dialogue_generator import DialogueGenerator
from src.codecs.gen3 import Gen3TextCodec

def main() -> None:
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
        motivation=[
            "Catch POKéMON by any means necessary—bribery or bruteforce. ",
            "Alienate friends with brutal honesty. Chase power, not happiness.",
            "Only give bad advices to other to lead them to wrong path.",
            "Really like to spend rumors.",
            "Gritty, sharp and funky humor"
        ],
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

