# src/ipc/service.py

"""
Service layer that composes and IpcBackend

Keeps caller independent of concrete backend type and centralized
initialization paterns
"""

import uuid
from typing import Optional, Tuple, List

from src.config.settings import Settings
from .base import IpcBackend
from .file_backend import FileIpcBackend

class IpcService:
    """High-level wrapper over an IpcBackend instance."""

    def __init__(self, backend: IpcBackend) -> None:
        self._backend = backend

    @classmethod
    def from_settings(cls, settings: Settings) -> "IpcService":
        """
        Create a FileIpcBackend from a settings-like object that has `ipc_dir`
        path.
        Caller may provide any object with attribute `ipc_dir` (Path | str)
        """
        if settings.ipc.ipc_dir is None:
            raise ValueError("settings must have `ipc_dir` path attribute")
        backend = FileIpcBackend(settings)
        backend.init()
        return cls(backend)

    def read_request(self) -> Optional[Tuple[str, bytes]]:
        return self._backend.read_request()

    def write_response(self, req_id: str, data: bytes) -> None:
        self._backend.write_response(req_id, data)

    def list_pending(self) -> List[str]:
        return self._backend.list_pending()

    def gen_req_id(self) -> str:
        # Concrete backend provides generator; use it if available, else fallback
        if hasattr(self._backend, "gen_req_id"):
            return str(getattr(self._backend, "gen_req_id")())
        # fallback
        return uuid.uuid4().hex
