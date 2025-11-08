import logging
from pathlib import Path
from .decode import decode

logger = logging.getLogger(__file__)


def get_id(data: bytes | bytearray | str | Path) -> bytes:
    decoded = decode(data, partial_decode=True)
    id = decoded[-16:]
    return bytes(id)
