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
class LlmConfig:
    model_path: Path
    n_ctx: int = 4096
    temperature: float = 1.2
    top_k: int = 50
    top_p: float = 0.92
    repeat_penalty: float = 1.1

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
        return cls(
            extract=ExtractConfig(
                rom_path=Path(config['extract']['rom_path']),
                output_path=Path(config['extract']['output_path']),
                start_offset=config['extract']['start_offset'],
                end_offset=config['extract']['end_offset']
            ),
            llm=LlmConfig(
                model_path=Path(config['llm']['model_path']),
                n_ctx=config['llm']['n_ctx'],
                temperature=config['llm']['temperature'],
                top_k=config['llm']['top_k'],
                top_p=config['llm']['top_p'],
                repeat_penalty=config['llm']['repeat_penalty']
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
                    'model_path': str(self.llm.model_path),
                    'n_ctx': self.llm.n_ctx,
                    'temperature': self.llm.temperature,
                    'top_k': self.llm.top_k,
                    'top_p': self.llm.top_p,
                    'repeat_penalty': self.llm.repeat_penalty
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

