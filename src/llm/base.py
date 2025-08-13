from abc import abstractmethod
from typing import Any

class LlmClient():
    """Protocol for any LLM client implementation."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        *,
        max_tokens: int = 60,
        stop: Optional[Iterable[str]] = None,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        **kwargs: Any,
    ) -> str:
       """
        Generate text continuation for the given prompt.

        :param prompt: The text prompt to send to the model.
        :param max_tokens: Maximum number of output tokens.
        :param stop: Optional list of stop sequences.
        :return: Generated text (stripped of whitespace).
        """
        ...
