from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Tuple, List

"""
IPC backend interface.

A backend implements basic operations the service will call.
"""
class IpcBackend(ABC):
    """Abstract interface for IPC Backend"""

    @abstractmethod
    def init(self) -> None:
        """ Prepare the backend """
        raise NotImplementedError

    @abstractmethod
    def read_request(self) -> Optional[Tuple[str, bytes]]:
        """ Read and return the next pending request.

        Returns:
            Tuple (req_id, payload) or None if no request

        """
        raise NotImplementedError

    @abstractmethod
    def write_response(self, req_id: str, data: bytes) -> None:
        """ Atomically write a response for the provided request id, """
        raise NotImplementedError

    @abstractmethod
    def list_pending(self) -> List[str]:
        """ Return list of request ids for which response files exist. """
        raise NotImplementedError

