"""LEB128 encoding/decoding utilities."""

import leb128


def encode(value: int) -> bytes:
    """
    Encode integer to LEB128 unsigned format.

    Args:
        value: Integer to encode

    Returns:
        LEB128 encoded bytes
    """
    return leb128.u.encode(value)


def decode(data: bytes) -> int:
    """
    Decode LEB128 unsigned format to integer.

    Args:
        data: LEB128 encoded bytes

    Returns:
        Decoded integer
    """
    return leb128.u.decode(data)


def get_leb128_length(data: bytes) -> int:
    """
    Get the length of a LEB128 encoded value.

    Args:
        data: LEB128 encoded bytes

    Returns:
        Length in bytes of the LEB128 value
    """
    for i, byte in enumerate(data):
        if byte < 128:
            return i + 1
    raise ValueError("Failed to get LEB128 length")

