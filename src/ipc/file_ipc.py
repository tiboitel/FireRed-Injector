import os
import uuid
from pathlib import Path
from typing import Tuple, List, Optional

IPC_DIR = Path("/home/tiboitel/Downloads/shared_ipc")

def init_ipc(ipc_dir: Path = IPC_DIR) -> None:
    ipc_dir.mkdir(parents=True, exist_ok=True)

def read_request(ipc_dir: Path = IPC_DIR) -> Optional[Tuple[str, bytes]]:
    for path in ipc_dir.glob("dialog_in_*.bin"):
        req_id = path.stem.split("_", 2)[2]
        with open(path, "rb") as f:
            bytes = f.read()
        path.unlink(missing_ok=True)
        return req_id, bytes
    return None

def write_response(req_id: str, data: bytes, ipc_dir: Path = IPC_DIR) -> None:
    tmp_path = ipc_dir / f"dialog_out_{req_id}.tmp"
    final_path = ipc_dir / f"dialog_out_{req_id}.bin"
    with open(tmp_path, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, final_path)

def poll_responses(ipc_dir: Path = IPC_DIR) -> List[str]:
    ids: List[str] = []
    for path in ipc_dir.glob("dialog_out_*.bin"):
        req_id = path.stem.split("_", 2)[2]
        ids.append(req_id)
    return ids

def gen_req_id() -> str:
    return uuid.uuid4().hex

