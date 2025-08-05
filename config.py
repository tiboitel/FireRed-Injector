from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class ExtractConfig:
    rom_path: Path
    output_path: Path
    start_offset: int
    end_offset: int

@dataclass(frozen=True)
class LlmConfig:
    model_path: Path
    n_ctx: int = 4096
    temperature: float = 1.2
    top_k: int = 50
    top_p: float = 0.92
    repeat_penalty: float = 1.1
