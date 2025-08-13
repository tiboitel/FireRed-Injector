# src/ipc/file_backend.py

import logging
import os
import time
import uuid
from typing import Tuple, List, Optional
from .base import IpcBackend
from src.config.settings import Settings

# should maybe externalize that in settings
IPC_IN_PREFIX = "ipc_in_"
IPC_OUT_PREFIX = "ipc_out_"
IPC_SUFFIX = ".bin"

class FileIpcBackend(IpcBackend):
    """ A file-backed IPC backend. """
    def __init__(self, settings: Settings) -> None:
        self.settings = settings.ipc

    def init(self) -> None:
        """ Create directory and clean stale files. """
        self.settings.ipc_dir.mkdir(parents=True, exist_ok=True)
        try:
            self.settings.ipc_dir.chmod(0o700)
        except PermissionError:
            logging.info("Unable to chmod ipc_dir %s", self.settings.ipc_dir,
                         exc_info=True)
        self._cleanup_stale()

    def read_request(self) -> Optional[Tuple[str, bytes]]:
        """
        Read the oldest pending request (FIFO by mtime)

        Read the file, then attempt to remove it so the request is consumed.
        """
        self._cleanup_stale()
        candidates = [
            p for p in self.settings.ipc_dir.iterdir()
            if p.is_file() and p.name.startswith(IPC_IN_PREFIX) and
                p.name.endswith(IPC_SUFFIX)
        ]
        if not candidates:
            return None

        candidates.sort(key=lambda p: p.stat().st_mtime)
        for path in candidates:
            req_id = path.name[len(IPC_IN_PREFIX): -len(IPC_SUFFIX)]
            try:
                with open(path, "rb") as f:
                    payload = f.read()
            except (FileNotFoundError, PermissionError, OSError) as exc:
                logging.error("Error: could not read request %s: %s", path, exc)
                continue
            # remove requested file after readed
            try:
                path.unlink()
            except FileNotFoundError:
                logging.info("Request file already remove %s", path)
            except Exception:
                logging.info("Failed to unlink request file %s", path,
                             exc_info=True)
            return req_id, payload
        return None

    def write_response(self, req_id: str, data: bytes) -> None:
        tmp_name = f"{IPC_OUT_PREFIX}{req_id}.tmp.{uuid.uuid4().hex}"
        tmp_path = self.settings.ipc_dir / tmp_name
        final_path = self.settings.ipc_dir / f"{IPC_OUT_PREFIX}{req_id}{IPC_SUFFIX}"

        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        fd = None
        try:
            old_umask = os.umask(0)
            try:
                fd = os.open(str(tmp_path), flags, 0o600)
            finally:
                os.umask(old_umask)

            with os.fdopen(fd, "wb") as f:
                fd = None
                f.write(data)
                f.flush()
                try:
                    os.fsync(f.fileno())
                except (AttributeError, OSError):
                    logging.info("fsync failed / unsupported for %s", tmp_path, exc_info=True)

            # Atomic replace
            os.replace(str(tmp_path), str(final_path))

            # CHMOD final file to 0o600
            try:
                final_path.chmod(0o600)
            except PermissionError:
                logging.error("Error: cannot chmod response file %s", final_path, exc_info=True)
        finally:
            # Clean up if tmp file exists and hold fd
            if fd is not None:
                try:
                    os.close(fd)
                except Exception:
                    pass
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except Exception:
                    logging.info("Failed to remove tmp ipc file %s", tmp_path, exc_info=True)

    def list_pending(self) -> List[str]:
        """ Return list of req_ids which have response file present """
        self._cleanup_stale()
        ids: List[str] = []
        for p in self.settings.ipc_dir.iterdir():
            if not p.is_file():
                continue
            if p.name.startswith(IPC_OUT_PREFIX) and p.name.endswith(IPC_SUFFIX):
                req_id = p.name[len(IPC_OUT_PREFIX):-len(IPC_SUFFIX)]
                ids.append(req_id)
            return ids
        return ids

    def _cleanup_stale(self) -> None:
        """ Remove files older than TTL (TTL > 0) """
        if self.settings.ttl <= 0:
            return
        now = time.time()
        for p in list(self.settings.ipc_dir.iterdir()):
            if not p.is_file():
                continue
            try:
                mtime = p.stat().st_mtime
            except OSError:
                # Should log error ?
                continue
            if (now - mtime) > self.settings.ttl:
                try:
                    p.unlink()
                    logging.info("Removed stale IPC file: %s", p)
                except Exception:
                    logging.error("Error: failed to remove stale file %s", p,
                                  exc_info=True)

    @staticmethod
    def gen_req_id() -> str:
        req_id = uuid.uuid4().hex
        return req_id
