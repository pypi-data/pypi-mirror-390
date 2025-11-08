import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__file__)


def to_bytes(data: bytes | bytearray | str | Path) -> bytes:
    if isinstance(data, (bytes, bytearray)):
        return bytes(bytearray(data))
    elif isinstance(data, (str, Path)):
        with open(data, "rb") as f:
            return f.read()
    else:
        raise TypeError("Expected bytes, bytearray, or file path (str/Path).")


def run_tool(command: str):
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        shell=True,  # kept getting FileNotFound for long filenames w/ shell=False + commmand list[]
    )

    if result.stdout:
        for line in result.stdout.splitlines():
            logger.debug(line)

    if result.stderr:
        for line in result.stderr.splitlines():
            logger.error(line)

    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, command)


# expose methods directly
from .decode import decode, decompress
from .encode import encode
from .get_id import get_id

__all__ = ["decode", "decompress", "encode", "get_id"]
