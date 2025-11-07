"""Address encoding and decoding functions."""

from .address import Address
from .base32 import decode as base32_decode, encode as base32_encode
from .checksum import get_checksum
from .enums import CoinType, Protocol
from .leb128_utils import decode as leb128_decode, encode as leb128_encode
from .validation import check_address_string


def decode(address: str) -> Address:
    """
    Decode an address string to an Address object.

    Args:
        address: Address string (e.g., "f1...", "t1...", "f410f...")

    Returns:
        Address object

    Raises:
        ValueError: If address is invalid
    """
    address_data = check_address_string(address)
    protocol = Protocol(address_data["protocol"])
    payload = address_data["payload"]
    coin_type = CoinType(address_data["coinType"])
    return Address(
        leb128_encode(protocol.value) + payload, coin_type
    )


def encode(coin_type: str, address: Address) -> str:
    """
    Encode an Address object to a string.

    Args:
        coin_type: Coin type prefix ("f" or "t")
        address: Address object

    Returns:
        Address string

    Raises:
        ValueError: If address is invalid
    """
    if not address or not address.bytes:
        raise ValueError("Invalid address")

    protocol = address.protocol()
    payload = address.payload()
    prefix = f"{coin_type}{protocol.value}"

    if protocol == Protocol.ID:
        id_value = leb128_decode(payload)
        return f"{prefix}{id_value}"

    elif protocol == Protocol.DELEGATED:
        namespace = address.namespace
        sub_addr_bytes = address.sub_addr
        protocol_byte = leb128_encode(protocol.value)
        namespace_byte = leb128_encode(namespace)
        checksum_bytes = get_checksum(protocol_byte + namespace_byte + sub_addr_bytes)
        bytes_data = sub_addr_bytes + checksum_bytes
        return f"{prefix}{namespace}f{base32_encode(bytes_data)}"

    else:
        # SECP256K1, ACTOR, BLS
        checksum = get_checksum(address.bytes)
        bytes_data = payload + checksum
        return f"{prefix}{base32_encode(bytes_data)}"


def new_from_string(address: str) -> Address:
    """
    Create an Address from a string (convenience function).

    Args:
        address: Address string

    Returns:
        Address object
    """
    return decode(address)

