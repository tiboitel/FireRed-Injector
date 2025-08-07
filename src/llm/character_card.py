from dataclasses import dataclass
from typing import List

@dataclass
class CharacterCard:
    name: str
    age: int
    location: str
    traits: List[str]
    motivation: List[str]

