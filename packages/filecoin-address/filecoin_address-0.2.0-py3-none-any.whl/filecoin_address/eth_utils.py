"""Ethereum address utilities."""

from eth_utils import (
    is_address as eth_is_address,
    is_hexstr as eth_is_hex_string,
    to_checksum_address,
    to_bytes,
)

# Ethereum address length (20 bytes)
ETH_ADDRESS_LENGTH = 20

# Ethereum ID mask prefix length (12 bytes)
ETH_ID_MASK_PREFIX_LENGTH = 12

# Ethereum ID mask prefix: 0xFF followed by 11 zeros
ETH_ID_MASK_PREFIX = bytes([255] + [0] * 11)


def is_eth_address(address: str) -> bool:
    """
    Determine if the input is a valid Ethereum address.

    Args:
        address: String to check

    Returns:
        True if valid Ethereum address, False otherwise
    """
    if not eth_is_hex_string(address):
        return False
    if not eth_is_address(address):
        return False
    # Check that address is not zero
    try:
        # Remove 0x prefix if present for int conversion
        hex_str = address[2:] if address.startswith("0x") else address
        if int(hex_str, 16) == 0:
            return False
    except ValueError:
        return False
    return True


def is_eth_id_mask_address(eth_addr: str) -> bool:
    """
    Determine if the input is an Ethereum ID mask address.

    ID mask addresses have the format: 0xFF followed by 11 zeros, then 8 bytes for ID.

    Args:
        eth_addr: Ethereum address string to check

    Returns:
        True if ID mask address, False otherwise
    """
    if not is_eth_address(eth_addr):
        return False

    bytes_addr = to_bytes(hexstr=eth_addr)
    prefix = bytes_addr[:ETH_ID_MASK_PREFIX_LENGTH]
    return prefix == ETH_ID_MASK_PREFIX


def get_eth_address_bytes(eth_addr: str) -> bytes:
    """
    Get bytes from Ethereum address string.

    Args:
        eth_addr: Ethereum address string (with or without 0x prefix)

    Returns:
        20-byte address
    """
    return to_bytes(hexstr=eth_addr)


def to_checksum_eth_address(eth_addr: str) -> str:
    """
    Convert Ethereum address to checksummed format (EIP-55).

    Args:
        eth_addr: Ethereum address string

    Returns:
        Checksummed Ethereum address
    """
    return to_checksum_address(eth_addr)

