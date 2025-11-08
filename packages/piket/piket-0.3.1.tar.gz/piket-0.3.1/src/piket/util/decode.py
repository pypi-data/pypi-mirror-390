import logging
from pathlib import Path
from piket import NEDCENC, NEVPK
from piket.constants import VPK_SIZE, VPK
from . import to_bytes, run_tool

logger = logging.getLogger(__file__)
PARENT = NEDCENC.parent.resolve()


def decode(data: bytes | bytearray | str | Path, partial_decode: bool = False) -> bytearray:
    # handle all input types
    data = to_bytes(data)
    file = NEDCENC.parent.resolve() / "in.raw"
    logger.debug(f"Writing .raw data to '{file}'.")
    file.write_bytes(data)

    # decode .raw to .bin (includes a vpk compression block which we will extract)
    decoded_path = PARENT / "decoded.bin"
    logger.debug(f"Running nedcenc, output to '{decoded_path}'.")
    run_tool(f'"{NEDCENC}" -i "{file}" -d -o "{decoded_path}"')
    logger.debug(f"Removing '{file}'.")
    file.unlink()
    if not decoded_path.exists():
        raise Exception("nedcenc did not output a file.")

    decoded = decoded_path.read_bytes()
    logger.debug(f"Removing '{decoded_path}'.")
    decoded_path.unlink()

    if partial_decode:
        return bytearray(decoded)

    data = decompress(decoded)

    logger.info("Conversion from .raw to .bin (decompressed) complete.")
    return bytearray(data)


def decompress(decoded: bytes) -> bytes:
    # trim the decoded .bin to the vpk block (compressed level data)
    logger.debug("Trimming decoded .raw data to VPK block.")
    size = int.from_bytes(decoded[VPK_SIZE : VPK_SIZE + 2], "little")
    trimmed_path = PARENT / "trimmed.vpk"
    trimmed_path.write_bytes(decoded[VPK : VPK + size])

    # decompress the vpk block into pure level data (.bin again)
    decompressed_path = PARENT / "out.bin"
    logger.debug(f"Running nevpk, output to '{decompressed_path}'.")
    run_tool(f'"{NEVPK}" -i "{trimmed_path}" -d -o "{decompressed_path}"')
    logger.debug(f"Removing '{trimmed_path}'.")
    trimmed_path.unlink()

    if not decompressed_path.exists():
        raise Exception("nevpk did not output a file.")

    data = decompressed_path.read_bytes()
    logger.debug(f"Removing '{decompressed_path}'.")
    decompressed_path.unlink()

    return data
