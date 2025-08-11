# src/ipc/file_ipc.py
import os
from pathlib import Path
from typing import Tuple, List, Optional
from src.config.settings import Settings

def init_ipc(settings: Settings) -> None:
    settings.ipc_dir.mkdir(parents=True, exist_ok=True)
    print(settings.ipc_dir)

def read_request(settings: Settings) -> Optional[Tuple[str, bytes]]:
    for path in settings.ipc_dir.glob("dialog_in_*.bin"):
        req_id = path.stem.split("_", 2)[2]
        with open(path, "rb") as f:
            bytes = f.read()
        path.unlink(missing_ok=True)
        return req_id, bytes
    return None

def write_response(settings: Settings, req_id: str, data: bytes) -> None:
    tmp_path = settings.ipc_dir / f"dialog_out_{req_id}.tmp"
    final_path = settings.ipc_dir / f"dialog_out_{req_id}.bin"
    with open(tmp_path, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, final_path)

def poll_responses(settings: Settings) -> List[str]:
    ids: List[str] = []
    for path in settings.ipc_dir.glob("dialog_out_*.bin"):
        req_id = path.stem.split("_", 2)[2]
        ids.append(req_id)
    return ids

def gen_req_id() -> str:
    return uuid.uuid4().hex

