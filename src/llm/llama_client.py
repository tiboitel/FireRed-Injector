from typing import Any
from llama_cpp import Llama, CreateCompletionResponse
from src.llm.base import LlmClient
from src.config.settings import LlmConfig

class LlamaClient(LlmClient):
    """LlmClient implementation for llama_cpp."""

    def __init__(self, cfg: LlmConfig):
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
        stop: Any = None,
        **kwargs: Any,
    ) -> str:
        """
        Call the underlying Llama model and return its output.
        """
        raw: Any = \
            self.llm(
                prompt,
                max_tokens=max_tokens,
                stop=stop or ["\n"],
                **kwargs
            )

        # Normalize to a single response dict
        resp: CreateCompletionResponse
        if isinstance(raw, (list, tuple)):
            resp = raw[0]
        else:
            resp = raw

        # Now extract the text
        choices = resp.get("choices")
        if not isinstance(choices, list) or len(choices) == 0:
            raise RuntimeError("LLM returned no choices")
        first = choices[0]
        if not isinstance(first, dict) or "text" not in first:
            raise RuntimeError("Unexpected LLM response structure")
        text = first["text"]
        if not isinstance(text, str):
            raise RuntimeError("LLM choice text is not a string")
        return text.strip()

