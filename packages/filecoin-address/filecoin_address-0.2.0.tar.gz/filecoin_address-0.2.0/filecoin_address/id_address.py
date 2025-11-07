"""ID address utilities for Filecoin ID addresses (f0...)."""

import struct

from .address import Address
from .address_creation import new_id_address
from .enums import CoinType, Protocol
from .eth_utils import (
    ETH_ADDRESS_LENGTH,
    ETH_ID_MASK_PREFIX,
    ETH_ID_MASK_PREFIX_LENGTH,
    is_eth_id_mask_address,
    to_checksum_eth_address,
)
from .leb128_utils import decode as leb128_decode
from .encoding import decode


def id_from_address(address: Address) -> int:
    """
    Extract the numerical ID from an ID address.

    Args:
        address: Address object (must be ID protocol)

    Returns:
        ID number

    Raises:
        ValueError: If address is not an ID address
    """
    if address.protocol() != Protocol.ID:
        raise ValueError("Cannot get ID from non ID address")
    return id_from_payload(address.payload())


def id_from_payload(payload: bytes) -> int:
    """
    Extract the numerical ID from an ID address payload.

    Args:
        payload: Payload bytes from ID address

    Returns:
        ID number
    """
    return leb128_decode(payload)


def id_from_eth_address(eth_addr: str, coin_type: CoinType = CoinType.MAIN) -> str:
    """
    Derive the f0 address from an Ethereum ID mask address.

    Ethereum ID mask addresses have the format:
    - First 12 bytes: 0xFF followed by 11 zeros
    - Last 8 bytes: ID number (big-endian)

    Args:
        eth_addr: Ethereum ID mask address (e.g., 0xFF00000000000000000000000000000000000023)
        coin_type: Network coin type (default: MAIN)

    Returns:
        Filecoin ID address string (e.g., "f01035")

    Raises:
        ValueError: If address is not an ID mask address
    """
    if not is_eth_id_mask_address(eth_addr):
        raise ValueError("Cannot convert non-ID mask address to id")

    from .eth_utils import get_eth_address_bytes

    bytes_addr = get_eth_address_bytes(eth_addr)
    # Extract the ID from bytes 12-20 (8 bytes, big-endian)
    id_bigint = struct.unpack(">Q", bytes_addr[ETH_ID_MASK_PREFIX_LENGTH:])[0]
    return new_id_address(id_bigint, coin_type).to_string()


def eth_address_from_id(id_address: str) -> str:
    """
    Derive the Ethereum ID mask address from an f0 address.

    Creates an Ethereum address with format:
    - First 12 bytes: 0xFF followed by 11 zeros
    - Last 8 bytes: ID number (big-endian)

    Args:
        id_address: Filecoin ID address (e.g., "f01035")

    Returns:
        Ethereum ID mask address with checksum (e.g., "0xFF00000000000000000000000000000000000023")
    """
    address = decode(id_address)
    id_value = id_from_address(address)

    # Create 20-byte buffer
    buffer = bytearray(ETH_ADDRESS_LENGTH)
    # Set first byte to 0xFF
    buffer[0] = 255
    # Set ID in bytes 12-20 (big-endian, 8 bytes)
    struct.pack_into(">Q", buffer, ETH_ID_MASK_PREFIX_LENGTH, id_value)

    eth_address = f"0x{buffer.hex()}"
    return to_checksum_eth_address(eth_address)

