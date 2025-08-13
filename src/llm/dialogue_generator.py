import time
from src.llm.base import LlmClient, RetryableProviderError
from src.config.settings import CharacterCard, LlmConfig
from src.llm.prompt_builder import PromptBuilder

class DialogueGenerator:
    def __init__(
        self,
        llm_client: LlmClient,
        character: CharacterCard,
        prompt_builder: PromptBuilder,
        llm_cfg: LlmConfig | None = None,
    ):
        self.llm = llm_client
        self.character = character
        self.builder = prompt_builder
        self.retry_cfg = (llm_cfg.retry if llm_cfg else None)

    def generate(self, original_line: str) -> str:
        prompt = self.builder.build(self.character, original_line)

        attempts = 1
        max_attempts = self.retry_cfg.max_attempts if self.retry_cfg else 1
        backoff = self.retry_cfg.initial_backoff if self.retry_cfg else 0.0
        mult = self.retry_cfg.backoff_multiplier if self.retry_cfg else 1.0

        while True:
            try:
                raw = self.llm.generate(
                    prompt,
                    max_tokens=64,
                    stop=["\n"],
                )
                return raw.strip().strip("“”")
            except RetryableProviderError:
                if attempts >= max_attempts:
                    raise
                if backoff > 0:
                    time.sleep(backoff)
                    backoff *= mult
                attempts += 1

