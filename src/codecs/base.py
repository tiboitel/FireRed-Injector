from abc import ABC, abstractmethod

class TextCodec(ABC):
    @abstractmethod
    def decode(self, data: bytes) -> str:
        ...

    @abstractmethod
    def encode(self, text: str, max_len: int = 255) -> bytes:
        ...
