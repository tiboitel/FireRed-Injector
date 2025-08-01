import json
from pathlib import Path
from src.loaders.base import ByteSource
from src.codecs.base import TextCodec

class DialogExtractor:
    def __init__(
        self,
        source: ByteSource,
        codec: TextCodec,
        start: int,
        end: int,
    ):
        self.source = source
        self.codec = codec
        self.start = start
        self.end = end


    def extract(self) -> dict[str, str]:
        result: dict[str, str] = {}
        offset = self.start
        terminators = {0xFB, 0xFF}

        while offset < self.end:
            chunk = self.source.read(offset, 255)
            try:
                idx = next(i for i, b in enumerate(chunk) if b in terminators)
            except StopIteration:
                offset += 1
                continue
            segment = chunk[: idx + 1]
            text = self.codec.decode(segment).strip()
            if text:
                result[segment.hex()] = text
            offset += idx + 1

        return result

    def save(self, dialog_map: dict[str, str], path: Path) -> None:
        path.write_text(json.dumps(dialog_map, ensure_ascii=False, indent=2), encoding="utf-8")
