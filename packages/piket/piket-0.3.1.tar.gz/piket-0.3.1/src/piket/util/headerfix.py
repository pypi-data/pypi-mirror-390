# python re-implementation of BlackShark's headerfix.c
# BlackShark: https://github.com/Bl4ckSh4rk
# headerfix.c: https://github.com/HunterRDev/e-ReaderCardCreator/blob/master/AC_e-Reader_Card_Creator/Decompression/External/Source%20Code/headerfix.c

HEADER_SIZE = 0x30
SIGNATURE = b"NINTENDO"


def _get_data_checksum(data: bytes) -> int:
    total = 0
    for i in range(0, len(data), 2):
        hi = data[i]
        lo = data[i + 1] if i + 1 < len(data) else 0
        total += (hi << 8) + lo
    return (~total) & 0xFFFF


def _get_header_checksum(header: bytearray) -> int:
    xor = header[0xC] ^ header[0xD] ^ header[0x10] ^ header[0x11]
    for i in range(0x26, 0x2D):
        xor ^= header[i]
    return xor & 0xFF


def _get_global_checksum(header: bytes, data: bytes) -> int:
    total = sum(header[:0x2F])
    for i in range(0, len(data), 0x30):
        xor = 0
        for b in data[i : i + 0x30]:
            xor ^= b
        total += xor
    return (~total) & 0xFF


def headerfix(input_data: bytes | bytearray) -> bytes:
    """
    Fixes the header of a decoded e-Reader card.

    Args:
        input_data (bytes or bytearray): Full contents of the e-Card.

    Returns:
        bytes: A new bytes object with updated header checksums.

    Raises:
        ValueError: If the input is invalid or corrupted.
    """
    if not isinstance(input_data, (bytes, bytearray)):
        raise TypeError("Input must be bytes or bytearray")

    if len(input_data) % HEADER_SIZE != 0 or len(input_data) <= HEADER_SIZE:
        raise ValueError("Invalid card size")

    buffer = bytearray(input_data)
    header = buffer[:HEADER_SIZE]

    if header[0x1A : 0x1A + 8] != bytearray(SIGNATURE):
        raise ValueError("Invalid e-Card signature")

    data_size = (header[0x06] << 8) + header[0x07]
    if data_size + HEADER_SIZE > len(buffer):
        raise ValueError("Data size in header exceeds buffer size")

    data = buffer[HEADER_SIZE : HEADER_SIZE + data_size]

    # checksums
    data_checksum = _get_data_checksum(data)
    header[0x13] = (data_checksum >> 8) & 0xFF
    header[0x14] = data_checksum & 0xFF

    header_checksum = _get_header_checksum(header)
    header[0x2E] = header_checksum

    global_checksum = _get_global_checksum(header, data)
    header[0x2F] = global_checksum

    return bytes(header + data)
