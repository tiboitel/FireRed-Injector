from abc import ABC, abstractmethod

class ByteSource(ABC):
    @abstractmethod
    def read(self, offset: int, size: int) -> bytes:
        ...

    @abstractmethod
    def size(self) -> int:
        ...

    @abstractmethod
    def read_u8(self, offset: int) -> int:
        ...

    @abstractmethod
    def read_u16(self, offset: int, *, little_endian: bool = True) -> int:
        ...

    @abstractmethod
    def read_u32(self, offset: int, *, little_endian: bool = True) -> int:
        ...

    @abstractmethod
    def read_pointer(self, offset: int, base_address: int = 0x08000000) -> int:
        ...
