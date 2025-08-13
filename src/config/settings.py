# src/config/settings.py
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List
import toml
import json

@dataclass
class ExtractConfig:
    rom_path: Path
    output_path: Path
    start_offset: int
    end_offset: int

@dataclass
class LlmRetryConfig:
    max_attempts: int = 3
    initial_backoff: float = 0.2
    backoff_multiplier: float = 2.0

@dataclass
class LlmConfig:
    model_path: Path
    n_ctx: int = 4096
    temperature: float = 1.2
    top_k: int = 50
    top_p: float = 0.92
    repeat_penalty: float = 1.1
    api_base: str = ""
    api_key: str = ""
    model: str = ""
    retry: LlmRetryConfig = field(default_factory=LlmRetryConfig)

@dataclass
class CharacterCard:
    name: str
    age: int
    location: str
    traits: List[str]
    motivation: List[str]

@dataclass
class IpcConfig:
    ipc_dir: Path
    ttl: int = 60

@dataclass
class Settings:
    extract: ExtractConfig
    llm: LlmConfig
    character: CharacterCard
    ipc: IpcConfig
    few_shot_examples: str = field(default_factory=str)

    @classmethod
    def from_toml(cls, path: Path) -> 'Settings':
        config = toml.load(path)
        llm_cfg = config['llm']
        retry_cfg = (llm_cfg.get('retry') or {})
        return cls(
            extract=ExtractConfig(
                rom_path=Path(config['extract']['rom_path']),
                output_path=Path(config['extract']['output_path']),
                start_offset=config['extract']['start_offset'],
                end_offset=config['extract']['end_offset'],
            ),
            llm=LlmConfig(
                provider=llm_cfg.get('provider', 'llama'),
                model_path=Path(llm_cfg['model_path']) if llm_cfg.get('model_path') else None,
                n_ctx=llm_cfg.get('n_ctx', 4096),
                temperature=llm_cfg.get('temperature', 1.2),
                top_k=llm_cfg.get('top_k', 50),
                top_p=llm_cfg.get('top_p', 0.92),
                repeat_penalty=llm_cfg.get('repeat_penalty', 1.1),
                api_base=llm_cfg.get('api_base', ''),
                api_key=llm_cfg.get('api_key', ''),
                model=llm_cfg.get('model', ''),
                retry=LlmRetryConfig(
                    max_attempts=retry_cfg.get('max_attempts', 3),
                    initial_backoff=retry_cfg.get('initial_backoff', 0.2),
                    backoff_multiplier=retry_cfg.get('backoff_multiplier', 2.0),
                )
            ),
            character=CharacterCard(**config['character']),
            ipc=IpcConfig(
                ipc_dir=Path(config['ipc']['ipc_dir']),
                ttl=config['ipc']['ttl']
            ),
            few_shot_examples=config['prompt']['few_shot_examples']
        )

    @classmethod
    def from_env(cls, settings: 'Settings') -> 'Settings':
        if 'ROM_PATH' in os.environ:
            settings.extract.rom_path = Path(os.environ['ROM_PATH'])
        if 'OUTPUT_PATH' in os.environ:
            settings.extract.output_path = Path(os.environ['OUTPUT_PATH'])
        if 'MODEL_PATH' in os.environ:
            settings.llm.model_path = Path(os.environ['MODEL_PATH'])
        if 'IPC_DIR' in os.environ:
            settings.ipc.ipc_dir = Path(os.environ['IPC_DIR'])
        return settings

    def save_runtime_config(self, path: Path) -> None:
        with open(path, 'w') as f:
            json.dump({
                'extract': {
                    'rom_path': str(self.extract.rom_path),
                    'output_path': str(self.extract.output_path),
                    'start_offset': self.extract.start_offset,
                    'end_offset': self.extract.end_offset
                },
                'llm': {
                    'provider': self.llm.provider,
                    'model_path': str(self.llm.model_path) if self.llm.model_path else "",
                    'n_ctx': self.llm.n_ctx,
                    'temperature': self.llm.temperature,
                    'top_k': self.llm.top_k,
                    'top_p': self.llm.top_p,
                    'repeat_penalty': self.llm.repeat_penalty,
                    'api_base': self.llm.api_base,
                    'api_key': self.llm.api_key,
                    'model': self.llm.model,
                    'retry': {
                        'max_attempts': self.llm.retry.max_attempts,
                        'initial_backoff': self.llm.retry.initial_backoff,
                        'backoff_multiplier': self.llm.retry.backoff_multiplier,
                    }
                },
                'character': {
                    'name': self.character.name,
                    'age': self.character.age,
                    'location': self.character.location,
                    'traits': self.character.traits,
                    'motivation': self.character.motivation
                },
                'ipc': {
                    'ipc_dir': str(self.ipc.ipc_dir),
                    'ttl': self.ipc.ttl
                },
                'few_shot_examples': self.few_shot_examples
            }, f, indent=2)

def load_settings(config_path: Path) -> Settings:
    settings = Settings.from_toml(config_path)
    settings = Settings.from_env(settings)
    return settings

