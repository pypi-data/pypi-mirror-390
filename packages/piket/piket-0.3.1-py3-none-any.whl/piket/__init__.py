import sys
import platform
import importlib.resources as resources
from pathlib import Path

_TOOLS = {
    "windows": {
        "libnedclib": "libnedclib.dll",
        "nedcenc": "nedcenc.exe",
        "nevpk": "nevpk.exe",
    },
    "macos": {
        "libnedclib": "libnedclib.dylib",
        "nedcenc": "nedcenc",
        "nevpk": "nevpk",
    },
    "linux": {
        "libnedclib": "libnedclib.so",
        "nedcenc": "nedcenc",
        "nevpk": "nevpk",
    },
}


def get_machine():
    os_name = sys.platform
    machine = platform.machine().lower()

    # Normalize OS name
    if os_name.startswith("linux"):
        os_name = "linux"
    elif os_name == "darwin":
        os_name = "macos"
    elif os_name in ("win32", "cygwin", "msys"):
        os_name = "windows"

    # Normalize architecture
    if machine in ("amd64", "x86_64"):
        arch = "amd64"
    elif machine in ("aarch64", "arm64"):
        arch = "arm64"
    else:
        arch = machine

    return f"{os_name}-{arch}"


# validate platform os support
machine = get_machine()
plat = machine[: machine.index("-")]
platform_tools = _TOOLS.get(plat)
if not platform_tools:
    raise OSError(f"Piket currently does not support: {machine}")

# resolve tool paths and expose them
_TOOL_PATHS: dict[str, Path] = {}
for tool, filename in platform_tools.items():
    try:
        with resources.path(f"piket.bin.{machine}", filename) as p:
            if not Path(p).exists():
                raise FileNotFoundError(f"Missing required tool: {tool}")
            _TOOL_PATHS[tool] = p
    except Exception as e:
        raise ImportError(f"Error loading binary '{filename}': {e}")

NEDCENC = _TOOL_PATHS["nedcenc"]
NEVPK = _TOOL_PATHS["nevpk"]

# expose methods and classes
from .util import decode, encode, get_id
from .card import Card
from .treasure import Treasure
from . import connecting_pikmin as ConnectingPikmin
from . import plucking_pikmin as PluckingPikmin
from . import marching_pikmin as MarchingPikmin

__all__ = [
    # tools
    "NEDCENC",
    "NEVPK",
    # direct methods
    "decode",
    "encode",
    "get_id",
    # primary classes
    "Card",
    "Treasure",
    # level classes
    "ConnectingPikmin",
    "PluckingPikmin",
    "MarchingPikmin",
]
