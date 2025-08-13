from __future__ import annotations
from typing import Any, Iterable, Optional
from src.llm.base import LlmClient

class DummyProvider(LlmClient):
    """A deterministic provider for tests & dev."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def generate(
        self,
        prompt: str,
        *,
        max_tokens: int = 60,
        stop: Optional[Iterable[str]] = None,
        **kwargs: Any,
    ) -> str:
        # Return a short predictable echo; tests can assert on this.
        text = f"[DUMMY]{prompt[:max_tokens]}"
        # naive stop handling for tests
        if stop:
            for s in stop:
                idx = text.find(s)
                if idx >= 0:
                    text = text[:idx]
                    break
        return text.strip()

