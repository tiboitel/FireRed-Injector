# tests/test_file_ipc.py
import os
import stat
import time
import threading
from pathlib import Path
from typing import Dict

import pytest

from src.config.settings import load_settings
from src.ipc.file_backend import FileIpcBackend, IPC_IN_PREFIX, IPC_OUT_PREFIX, IPC_SUFFIX

@pytest.fixture
def config_path(tmp_path):
    config = """
[extract]
rom_path = "gba_rom/fire_red.gba"
output_path = "data/dialog_map.json"
start_offset = 1191253
end_offset = 1722662

[llm]
model_path = "path/to/your/model"
n_ctx = 4096
temperature = 1.2
top_k = 50
top_p = 0.92
repeat_penalty = 1.1

[character]
name = "The Great Unknown"
age = 27
location = "All over the world"
traits = ["empty"]
motivation = [
    "No one care"
]

[ipc]
ipc_dir = "shared_ipc"
ttl=60

[prompt]
few_shot_examples = '''
Example:
'''

    """
    config_file = tmp_path / "config.toml"
    config_file.write_text(config)
    return config_file

def atomic_write_request(ipc_dir: Path, req_id: str, payload: bytes) -> None:
    """
    Simulate the Lua side: write to a tmp file then os.replace to final path.
    Use explicit 0o600 mode regardless of umask.
    """
    tmp = ipc_dir / f"{IPC_IN_PREFIX}{req_id}.tmp.{os.getpid()}.{time.time_ns()}"
    final = ipc_dir / f"{IPC_IN_PREFIX}{req_id}{IPC_SUFFIX}"
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    old_umask = os.umask(0)
    try:
        fd = os.open(str(tmp), flags, 0o600)
    finally:
        os.umask(old_umask)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(payload)
            f.flush()
            try:
                os.fsync(f.fileno())
            except Exception:
                pass
        os.replace(str(tmp), str(final))
        try:
            final.chmod(0o600)
        except Exception:
            pass
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except Exception:
                pass


def test_concurrent_requests_consumed(config_path, tmp_path):
    settings = load_settings(config_path)
    ipc_dir = tmp_path / "ipc"
    ipc_dir.mkdir()
    settings.ipc.ipc_dir = Path(ipc_dir)
    backend = FileIpcBackend(settings)
    backend.init()

    count = 30
    written: Dict[str, bytes] = {}
    threads = []
    for i in range(count):
        req_id = backend.gen_req_id()
        payload = f"payload-{i}".encode("utf-8")
        written[req_id] = payload
        t = threading.Thread(target=atomic_write_request, args=(ipc_dir, req_id, payload), daemon=True)
        threads.append(t)
        t.start()

    for t in threads:
        t.join(timeout=1.0)

    seen: Dict[str, bytes] = {}
    start = time.time()
    timeout = 5.0
    while len(seen) < count and (time.time() - start) < timeout:
        item = backend.read_request()
        if item:
            req_id, data = item
            assert req_id not in seen
            seen[req_id] = data
        else:
            time.sleep(0.01)

    assert len(seen) == count, f"consumed {len(seen)}/{count}"
    for k, v in written.items():
        assert k in seen and seen[k] == v

    remaining_in = list(ipc_dir.glob(f"{IPC_IN_PREFIX}*{IPC_SUFFIX}"))
    assert not remaining_in, f"leftover request files: {remaining_in}"


def test_stale_files_removed_on_init(config_path, tmp_path):
    settings = load_settings(config_path);
    ipc_dir = tmp_path / "ipc_stale"
    ipc_dir.mkdir()
    settings.ipc.ipc_dir = Path(ipc_dir)
    old_req = ipc_dir / f"{IPC_IN_PREFIX}old{IPC_SUFFIX}"
    old_resp = ipc_dir / f"{IPC_OUT_PREFIX}old{IPC_SUFFIX}"
    old_req.write_bytes(b"x")
    old_resp.write_bytes(b"x")
    old_time = time.time() - 3600
    os.utime(old_req, (old_time, old_time))
    os.utime(old_resp, (old_time, old_time))

    backend = FileIpcBackend(settings)
    backend.init()

    # Allow cleanup to run
    time.sleep(0.05)
    assert not any(ipc_dir.iterdir()), f"expected cleanup removed files, found: {list(ipc_dir.iterdir())}"


def test_write_response_permissions(config_path, tmp_path):
    settings = load_settings(config_path);
    ipc_dir = tmp_path / "ipc_perm"
    ipc_dir.mkdir()
    settings.ipc.ipc_dir = Path(ipc_dir)
    backend = FileIpcBackend(settings)
    backend.init()

    req_id = backend.gen_req_id()
    payload = b"answer"
    backend.write_response(req_id, payload)

    out = ipc_dir / f"{IPC_OUT_PREFIX}{req_id}{IPC_SUFFIX}"
    assert out.exists()
    assert out.read_bytes() == payload
    perm = stat.S_IMODE(out.stat().st_mode)
    assert perm == 0o600, f"expected 0o600, got {oct(perm)}"

