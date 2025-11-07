"""Conversion functions between Filecoin addresses and Ethereum addresses."""

from .address import Address
from .enums import CoinType, DelegatedNamespace, Protocol
from .eth_utils import (
    get_eth_address_bytes,
    is_eth_address,
    is_eth_id_mask_address,
    to_checksum_eth_address,
)
from .leb128_utils import encode as leb128_encode


def delegated_from_eth_address(
    eth_addr: str, coin_type: CoinType = CoinType.MAIN
) -> str:
    """
    Derive the f410 address from an Ethereum hex address.

    Args:
        eth_addr: Ethereum address (e.g., "0x1fa4cd...")
        coin_type: Network coin type (default: MAIN)

    Returns:
        Delegated Filecoin address string (e.g., "f410f...")

    Raises:
        ValueError: If Ethereum address is invalid or is an ID mask address
    """
    if not is_eth_address(eth_addr):
        raise ValueError("Invalid Ethereum address")
    if is_eth_id_mask_address(eth_addr):
        raise ValueError("Cannot convert ID mask to delegated address")

    return new_delegated_eth_address(eth_addr, coin_type).to_string()


def eth_address_from_delegated(delegated: str) -> str:
    """
    Derive the Ethereum address from an f410 address.

    Args:
        delegated: Delegated Filecoin address (e.g., "f410f...")

    Returns:
        Ethereum address with checksum (e.g., "0x1fa4cd...")

    Raises:
        ValueError: If address is not a delegated address or namespace is not EVM
    """
    from .encoding import decode

    address = decode(delegated)
    if address.protocol() != Protocol.DELEGATED:
        raise ValueError("Address is not a delegated address")

    namespace = address.namespace
    if namespace != DelegatedNamespace.EVM:
        raise ValueError(
            f"Expected namespace {DelegatedNamespace.EVM.value}, found {namespace}"
        )

    sub_addr_hex = address.sub_addr_hex
    eth_address = f"0x{sub_addr_hex}"

    # Add checksum
    eth_address = to_checksum_eth_address(eth_address)

    # Prevent returning an ID mask address
    if is_eth_id_mask_address(eth_address):
        raise ValueError("Delegated address invalid, represented ID mask address")

    return eth_address


def new_delegated_eth_address(
    eth_addr: str, coin_type: CoinType = CoinType.MAIN
) -> Address:
    """
    Create a delegated address from an Ethereum address.

    Args:
        eth_addr: Ethereum address (e.g., "0x1fa4cd...")
        coin_type: Network coin type (default: MAIN)

    Returns:
        Address object

    Raises:
        ValueError: If Ethereum address is invalid or is an ID mask address
    """
    from .address_creation import new_delegated_address

    if not is_eth_address(eth_addr):
        raise ValueError("Invalid Ethereum address")
    if is_eth_id_mask_address(eth_addr):
        raise ValueError("Cannot convert ID mask to delegated address")

    eth_bytes = get_eth_address_bytes(eth_addr)
    return new_delegated_address(DelegatedNamespace.EVM, eth_bytes, coin_type)

