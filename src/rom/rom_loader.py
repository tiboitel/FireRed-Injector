import os
import struct

class RomLoader:
    def __init__(self, path: str):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Rom file not found: {path}")

        with open(path, "rb") as f:
            self.rom = f.read()

        self.size = len(self.rom)
        print(f"[ROM] Loaded {self.size} bytes from {path}")

    def _check_bounds(self, offset: int, size: int = 1):
        if not (0 <= offset < self.size - size + 1):
            raise IndexError(f"Rom read out of bound: offset={hex(offset)} size={size}")

    def read_u8(self, offset: int) -> int:
        self._check_bounds(offset, 1)
        return self.rom[offset]

    def read_u16(self, offset: int) -> int:
        self._check_bounds(offset, 2)
        return struct.unpack_from("<H", self.rom, offset)[0]

    def read_u32(self, offset: int) -> int:
        self._check_bounds(offset, 4)
        return struct.unpack_from("<I", self.rom, offset)[0]

    def read_pointer(self, offset: int, base: int = 0x08000000) -> int:
        """Read a 32-bit little-endian pointer and convert to ROM offset (removes base)"""
        value = self.read_u32(offset)
        if value < base:
            raise ValueError(f"Invalid pointer: {hex(value)}")
        return value - base

    def read_bytes(self, offset: int, size: int) -> bytes:
        self._check_bounds(offset, size)
        return self.rom[offset:offset + size]

