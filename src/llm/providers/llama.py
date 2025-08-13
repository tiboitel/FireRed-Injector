from typing import Any, Iterable, Optional
from llama_cpp import Llama, CreateCompletionResponse
from src.llm.base import LlmClient, ProviderError, RetryableProviderError
from src.config.settings import LlmConfig

class LlamaClient(LlmClient):
    def __init__(self, cfg: LlmConfig):
        if not cfg.model_path:
            raise ProviderError("llama provider requires llm.model_path")
        try:
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
        except Exception as e:
            raise ProviderError(f"Failed to initialize llama: {e}") from e

    def generate(
        self,
        prompt: str,
        *,
        max_tokens: int = 127,
        stop: Optional[Iterable[str]] = None,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        **kwargs: Any,
    ) -> str:
        try:
            raw: Any = self.llm(
                prompt,
                max_tokens=max_tokens,
                stop=list(stop) if stop else ["\n"],
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                **kwargs,
            )
        except Exception as e:
            # Runtime issues often transient (OOM may be non-retryable; keep simple)
            raise RetryableProviderError(f"llama call failed: {e}") from e

        resp: CreateCompletionResponse = raw[0] if isinstance(raw, (list, tuple)) else raw
        choices = resp.get("choices")
        if not isinstance(choices, list) or not choices:
            raise ProviderError("llama returned no choices")
        first = choices[0]
        if not isinstance(first, dict) or "text" not in first or not isinstance(first["text"], str):
            raise ProviderError("Unexpected llama response structure")
        return first["text"].strip()

