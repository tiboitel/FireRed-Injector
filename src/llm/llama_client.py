from llama_cpp import Llama
from src.llm.base import LlmClient
from config import LlmConfig

class LlamaClient(LlmClient):
    """LlmClient implementation for llama_cpp."""

    def __init__(self, cfg: LlmConfig):
        """
        :param cfg: LlmConfig instance with model_path and generation hyperparameters.
        """
        # Initialize the underlying llama_cpp object
        self.llm = Llama(
            model_path=str(cfg.model_path),
            n_ctx=cfg.n_ctx,
            temperature=cfg.temperature,
            top_k=cfg.top_k,
            top_p=cfg.top_p,
            repeat_penalty=cfg.repeat_penalty,
            use_mmap=True,
            use_mlock=True,
        )

    def generate(
        self,
        prompt: str,
        max_tokens: int = 127,
        stop: list[str] | None = None,
        **kwargs
    ) -> str:
        """
        Call the underlying Llama model and return its output.
        Additional arguments can be passed through kwargs if needed.
        """
        response = self.llm(
            prompt,
            max_tokens=max_tokens,
            stop=stop or ["\n"],
            **kwargs
        )
        # Extract and return the generated text
        return response["choices"][0]["text"].strip()

