"""
Filecoin address manipulation routines for Python.

This module provides utilities for working with Filecoin addresses, including
validation, encoding, decoding, and conversion between native Filecoin addresses
and EVM delegated addresses.
"""

from .enums import CoinType, DelegatedNamespace, Protocol
from .address import Address
from .validation import (
    validate_address_string,
    check_address_string,
)
from .conversion import (
    delegated_from_eth_address,
    eth_address_from_delegated,
)
from .encoding import (
    decode,
    encode,
    new_from_string,
)
from .id_address import (
    eth_address_from_id,
    id_from_address,
    id_from_eth_address,
    id_from_payload,
)

__all__ = [
    # Enums
    "CoinType",
    "DelegatedNamespace",
    "Protocol",
    # Classes
    "Address",
    # Validation
    "validate_address_string",
    "check_address_string",
    # Conversion (Delegated addresses)
    "delegated_from_eth_address",
    "eth_address_from_delegated",
    # Conversion (ID addresses)
    "id_from_address",
    "id_from_payload",
    "id_from_eth_address",
    "eth_address_from_id",
    # Encoding
    "decode",
    "encode",
    "new_from_string",
]

__version__ = "0.1.0"

