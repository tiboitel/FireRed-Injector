from __future__ import annotations
from typing import Dict, Type
from src.config.settings import LlmConfig
from src.llm.base import LlmClient
from src.llm.providers.llama import LlamaClient
from src.llm.providers.dummy import DummyProvider

_REGISTRY: Dict[str, Type[LlmClient]] = {
    "llama": LlamaClient,
    "dummy": DummyProvider,
    # future: "ollama": OllamaProvider, "openai": OpenAIProvider, etc.
}

class LlmFactory:
    @staticmethod
    def create(provider_name: str, cfg: LlmConfig) -> LlmClient:
        key = provider_name.strip().lower()
        if key not in _REGISTRY:
            raise ValueError(f"Unknown LLM provider: {provider_name}")
        return _REGISTRY[key](cfg)

