"""Checksum calculation and validation for Filecoin addresses."""

import hashlib
from typing import Union


# Checksum hash length (4 bytes)
CHECKSUM_HASH_LENGTH = 4

# Payload hash length for SECP256K1 and ACTOR protocols (20 bytes)
PAYLOAD_HASH_LENGTH = 20


def get_checksum(ingest: Union[str, bytes]) -> bytes:
    """
    Calculate Blake2b checksum for address validation.

    Args:
        ingest: Data to checksum (bytes or string)

    Returns:
        4-byte checksum
    """
    if isinstance(ingest, str):
        ingest = ingest.encode("utf-8")

    # Use blake2b with 4-byte output
    hash_obj = hashlib.blake2b(ingest, digest_size=CHECKSUM_HASH_LENGTH)
    return hash_obj.digest()


def validate_checksum(data: Union[str, bytes], checksum: bytes) -> bool:
    """
    Validate checksum against data.

    Args:
        data: Data to validate (bytes or string)
        checksum: Expected checksum (4 bytes)

    Returns:
        True if checksum is valid, False otherwise
    """
    calculated = get_checksum(data)
    return calculated == checksum


def address_hash(ingest: bytes) -> bytes:
    """
    Calculate Blake2b hash for address payload.

    Used for SECP256K1 and ACTOR protocol addresses.

    Args:
        ingest: Data to hash

    Returns:
        20-byte hash
    """
    hash_obj = hashlib.blake2b(ingest, digest_size=PAYLOAD_HASH_LENGTH)
    return hash_obj.digest()

