from abc import ABC, abstractmethod
from typing import Dict

class Extractor(ABC):
    @abstractmethod
    def extract(self) -> Dict[str, str]:
        ...
