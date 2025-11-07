"""Address creation functions."""

from .address import Address
from .checksum import address_hash
from .enums import CoinType, Protocol
from .leb128_utils import encode as leb128_encode

# Maximum length of a delegated address's sub-address (54 bytes)
MAX_SUBADDRESS_LEN = 54


def new_address(
    protocol: Protocol, payload: bytes, coin_type: CoinType = CoinType.MAIN
) -> Address:
    """
    Create a new address from protocol and payload.

    Args:
        protocol: Address protocol
        payload: Address payload bytes
        coin_type: Network coin type (default: MAIN)

    Returns:
        Address object
    """
    protocol_byte = leb128_encode(protocol.value)
    bytes_data = protocol_byte + payload
    return Address(bytes_data, coin_type)


def new_id_address(id_value: int | str, coin_type: CoinType = CoinType.MAIN) -> Address:
    """
    Create a new ID address.

    Args:
        id_value: ID number (int or string)
        coin_type: Network coin type (default: MAIN)

    Returns:
        Address object
    """
    return new_address(Protocol.ID, leb128_encode(int(id_value)), coin_type)


def new_delegated_address(
    namespace: int, sub_addr: bytes, coin_type: CoinType = CoinType.MAIN
) -> Address:
    """
    Create a new delegated address.

    Args:
        namespace: Namespace number
        sub_addr: Sub-address bytes
        coin_type: Network coin type (default: MAIN)

    Returns:
        Address object

    Raises:
        ValueError: If sub-address is too long
    """
    if len(sub_addr) > MAX_SUBADDRESS_LEN:
        raise ValueError("Subaddress address length")
    namespace_byte = leb128_encode(namespace)
    payload = namespace_byte + sub_addr
    return new_address(Protocol.DELEGATED, payload, coin_type)


def new_actor_address(data: bytes, coin_type: CoinType = CoinType.MAIN) -> Address:
    """
    Create a new actor address.

    Args:
        data: Data to hash for address
        coin_type: Network coin type (default: MAIN)

    Returns:
        Address object
    """
    return new_address(Protocol.ACTOR, address_hash(data), coin_type)


def new_secp256k1_address(
    pubkey: bytes, coin_type: CoinType = CoinType.MAIN
) -> Address:
    """
    Create a new SECP256K1 address.

    Args:
        pubkey: Public key bytes
        coin_type: Network coin type (default: MAIN)

    Returns:
        Address object
    """
    return new_address(Protocol.SECP256K1, address_hash(pubkey), coin_type)


def new_bls_address(pubkey: bytes, coin_type: CoinType = CoinType.MAIN) -> Address:
    """
    Create a new BLS address.

    Args:
        pubkey: BLS public key (48 bytes)
        coin_type: Network coin type (default: MAIN)

    Returns:
        Address object
    """
    return new_address(Protocol.BLS, pubkey, coin_type)

