"""Address validation functions."""

from typing import Dict, Union

from .base32 import decode as base32_decode
from .checksum import CHECKSUM_HASH_LENGTH, validate_checksum
from .enums import CoinType, Protocol
from .leb128_utils import decode as leb128_decode, encode as leb128_encode

# Maximum length of a delegated address's sub-address (54 bytes)
MAX_SUBADDRESS_LEN = 54

# Maximum length of int64 as a string (19 characters)
MAX_INT64_STRING_LENGTH = 19

# BLS public key length (48 bytes)
BLS_PUBLIC_KEY_BYTES = 48

# Payload hash length for SECP256K1 and ACTOR protocols (20 bytes)
PAYLOAD_HASH_LENGTH = 20


def validate_address_string(address_string: str) -> bool:
    """
    Validate a Filecoin address string.

    Args:
        address_string: Address string to validate

    Returns:
        True if address is valid, False otherwise
    """
    try:
        check_address_string(address_string)
        return True
    except (ValueError, TypeError):
        return False


def check_address_string(address: str) -> Dict[str, Union[int, bytes, str]]:
    """
    Check and parse an address string, returning address data.

    Args:
        address: Address string to check

    Returns:
        Dictionary with keys: protocol, payload, bytes, coinType, namespace (if DELEGATED)

    Raises:
        ValueError: If address is invalid
        TypeError: If address is not a string
    """
    if not isinstance(address, str) or len(address) < 3:
        raise ValueError("Address should be a string of at least 3 characters")

    coin_type_str = address[0]
    if coin_type_str not in [ct.value for ct in CoinType]:
        valid_types = ", ".join([ct.value for ct in CoinType])
        raise ValueError(f"Address cointype should be one of: {valid_types}")

    try:
        protocol_num = int(address[1])
    except ValueError:
        raise ValueError(f"Invalid protocol character: {address[1]}")

    if protocol_num not in [p.value for p in Protocol]:
        valid_protocols = ", ".join([str(p.value) for p in Protocol])
        raise ValueError(f"Address protocol should be one of: {valid_protocols}")

    protocol = Protocol(protocol_num)
    protocol_byte = leb128_encode(protocol.value)
    raw = address[2:]

    if protocol == Protocol.ID:
        if len(raw) > MAX_INT64_STRING_LENGTH:
            raise ValueError("Invalid ID address length")
        try:
            id_value = int(raw)
        except ValueError:
            raise ValueError("Invalid ID address")
        payload = leb128_encode(id_value)
        bytes_data = bytes(protocol_byte + payload)
        return {
            "protocol": protocol.value,
            "payload": bytes(payload),
            "bytes": bytes_data,
            "coinType": coin_type_str,
        }

    elif protocol == Protocol.DELEGATED:
        split_index = raw.find("f")
        if split_index == -1:
            raise ValueError("Invalid delegated address")
        namespace_str = raw[:split_index]
        if len(namespace_str) > MAX_INT64_STRING_LENGTH:
            raise ValueError("Invalid delegated address namespace")
        sub_addr_cksm_str = raw[split_index + 1 :]
        sub_addr_cksm_bytes = base32_decode(sub_addr_cksm_str)
        if len(sub_addr_cksm_bytes) < CHECKSUM_HASH_LENGTH:
            raise ValueError("Invalid delegated address length")
        sub_addr_bytes = sub_addr_cksm_bytes[:-CHECKSUM_HASH_LENGTH]
        checksum_bytes = sub_addr_cksm_bytes[len(sub_addr_bytes) :]
        if len(sub_addr_bytes) > MAX_SUBADDRESS_LEN:
            raise ValueError("Invalid delegated address length")
        try:
            namespace_number = int(namespace_str)
        except ValueError:
            raise ValueError("Invalid delegated address namespace")
        namespace_byte = leb128_encode(namespace_number)
        payload = namespace_byte + sub_addr_bytes
        bytes_data = bytes(protocol_byte + payload)
        if not validate_checksum(bytes_data, checksum_bytes):
            raise ValueError("Invalid delegated address checksum")
        return {
            "protocol": protocol.value,
            "payload": bytes(payload),
            "bytes": bytes_data,
            "coinType": coin_type_str,
            "namespace": namespace_number,
        }

    elif protocol in (Protocol.SECP256K1, Protocol.ACTOR, Protocol.BLS):
        payload_cksm = base32_decode(raw)
        if len(payload_cksm) < CHECKSUM_HASH_LENGTH:
            raise ValueError("Invalid address length")
        payload = payload_cksm[:-CHECKSUM_HASH_LENGTH]
        checksum = payload_cksm[len(payload) :]

        # Validate payload length
        if protocol in (Protocol.SECP256K1, Protocol.ACTOR):
            if len(payload) != PAYLOAD_HASH_LENGTH:
                raise ValueError("Invalid address length")
        elif protocol == Protocol.BLS:
            if len(payload) != BLS_PUBLIC_KEY_BYTES:
                raise ValueError("Invalid address length")

        bytes_data = bytes(protocol_byte + payload)
        if not validate_checksum(bytes_data, checksum):
            raise ValueError("Invalid address checksum")
        return {
            "protocol": protocol.value,
            "payload": bytes(payload),
            "bytes": bytes_data,
            "coinType": coin_type_str,
        }

    else:
        raise ValueError(f"Invalid address protocol: {protocol.value}")

