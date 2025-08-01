import os
from struct import unpack
from src.loaders.base import ByteSource

class RomLoader(ByteSource):
    def __init__(self, path: str):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"ROM file not found: {path}")
        with open(path, 'rb') as f:
            self._data = f.read()

    def size(self) -> int:
        return len(self._data)

    def read(self, offset: int, size: int) -> bytes:
        if offset < 0 or offset + size > len(self._data):
            raise IndexError(f"Attempted out-of-bounds read at offset {offset}")
        return self._data[offset: offset + size]

    def read_u8(self, offset: int) -> int:
        return self.read(offset, 1)[0]

    def read_u16(self, offset: int, *, little_endian: bool = True) -> int:
        fmt = '<H' if little_endian else '>H'
        return unpack(fmt, self.read(offset, 2))[0]

    def read_u32(self, offset: int, *, little_endian: bool = True) -> int:
        fmt = '<I' if little_endian else '>I'
        return unpack(fmt, self.read(offset, 4))[0]

    def read_pointer(self, offset: int, base_address: int = 0x08000000) -> int:
        ptr = self.read_u32(offset, little_endian=True)
        return ptr - base_address
