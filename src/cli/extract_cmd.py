import logging
from config import ExtractConfig
from src.loaders.rom_loader import RomLoader
from src.codecs.gen3 import Gen3TextCodec
from src.extractors.dialog import DialogExtractor
from src.utils.io import save_json

def run_extraction(extract_cfg: ExtractConfig) -> None:
    loader = RomLoader(str(extract_cfg.rom_path))
    codec = Gen3TextCodec()
    extractor = DialogExtractor(loader, codec,
                                extract_cfg.start_offset,
                                extract_cfg.end_offset)
    raw_map = extractor.extract()
    save_json(raw_map, extract_cfg.output_path)
    logging.info(f"All dialogs saved to {extract_cfg.output_path}")

