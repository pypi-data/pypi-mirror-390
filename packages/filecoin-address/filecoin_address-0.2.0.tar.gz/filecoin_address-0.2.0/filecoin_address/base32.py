"""Base32 encoding/decoding with custom alphabet."""

# Base32 alphabet used by Filecoin: abcdefghijklmnopqrstuvwxyz234567
BASE32_ALPHABET = "abcdefghijklmnopqrstuvwxyz234567"


def _encode(buffer: bytes, alphabet: str) -> str:
    """Encode bytes to base32 string."""
    length = len(buffer)
    bits = 0
    value = 0
    output = ""

    for i in range(length):
        value = (value << 8) | buffer[i]
        bits += 8
        while bits >= 5:
            output += alphabet[(value >> (bits - 5)) & 31]
            bits -= 5

    if bits > 0:
        output += alphabet[(value << (5 - bits)) & 31]

    return output


def _decode(input_str: str, alphabet: str) -> bytes:
    """Decode base32 string to bytes."""
    # Remove padding if present
    input_str = input_str.replace("=", "")

    length = len(input_str)
    bits = 0
    value = 0
    index = 0
    output = bytearray((length * 5) // 8)

    for i in range(length):
        char_index = alphabet.find(input_str[i])
        if char_index < 0:
            raise ValueError(f"invalid base32 character: {input_str[i]}")
        value = (value << 5) | char_index
        bits += 5
        if bits >= 8:
            output[index] = (value >> (bits - 8)) & 255
            index += 1
            bits -= 8

    return bytes(output)


def encode(input_data: bytes | str) -> str:
    """
    Encode bytes or string to base32.

    Args:
        input_data: Bytes or string to encode

    Returns:
        Base32 encoded string
    """
    if isinstance(input_data, str):
        input_data = input_data.encode("utf-8")
    return _encode(input_data, BASE32_ALPHABET)


def decode(input_str: str) -> bytes:
    """
    Decode base32 string to bytes.

    Args:
        input_str: Base32 encoded string

    Returns:
        Decoded bytes

    Raises:
        ValueError: If input contains invalid base32 characters
    """
    # Validate all characters are in alphabet
    for char in input_str:
        if char not in BASE32_ALPHABET and char != "=":
            raise ValueError(f"invalid base32 character: {char}")

    return _decode(input_str, BASE32_ALPHABET)

