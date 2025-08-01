from src.llm.base import LlmClient
from src.llm.character_card import CharacterCard
from src.llm.prompt_builder import PromptBuilder

class DialogueGenerator:
    def __init__(
        self,
        llm_client: LlmClient,
        character: CharacterCard,
        prompt_builder: PromptBuilder
    ):
        self.llm = llm_client
        self.character = character
        self.builder = prompt_builder

    def generate(self, original_line: str) -> str:
        prompt = self.builder.build(self.character, original_line)
        raw = self.llm.generate(prompt)
        return raw.strip().strip("“”")

