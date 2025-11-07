"""Filecoin Address class."""

from .enums import CoinType, DelegatedNamespace, Protocol
from .leb128_utils import decode as leb128_decode, get_leb128_length


class Address:
    """Represents a Filecoin address."""

    def __init__(self, bytes_data: bytes, coin_type: CoinType = CoinType.MAIN):
        """
        Initialize Address from bytes.

        Args:
            bytes_data: Raw address bytes (protocol + payload)
            coin_type: Network coin type (default: MAIN)

        Raises:
            ValueError: If bytes are empty or protocol is invalid
        """
        if not bytes_data or len(bytes_data) == 0:
            raise ValueError("Missing bytes in address")

        self.bytes = bytes_data
        self._coin_type = coin_type

        # Validate protocol
        protocol_value = self.bytes[0]
        if protocol_value not in [p.value for p in Protocol]:
            raise ValueError(f"Invalid protocol {protocol_value}")

    def network(self) -> CoinType:
        """
        Get the network coin type.

        Returns:
            CoinType enum value
        """
        return self._coin_type

    def coin_type(self) -> CoinType:
        """
        Get the network coin type.

        Returns:
            CoinType enum value
        """
        return self._coin_type

    def protocol(self) -> Protocol:
        """
        Get the address protocol.

        Returns:
            Protocol enum value
        """
        return Protocol(self.bytes[0])

    def payload(self) -> bytes:
        """
        Get the address payload (bytes after protocol byte).

        Returns:
            Payload bytes
        """
        return self.bytes[1:]

    @property
    def namespace_length(self) -> int:
        """
        Get the length of the namespace in bytes (DELEGATED addresses only).

        Returns:
            Namespace length in bytes

        Raises:
            ValueError: If address is not DELEGATED protocol
        """
        if self.protocol() != Protocol.DELEGATED:
            raise ValueError("Can only get namespace length for delegated addresses")
        return get_leb128_length(self.payload())

    @property
    def namespace(self) -> int:
        """
        Get the namespace number (DELEGATED addresses only).

        Returns:
            Namespace number

        Raises:
            ValueError: If address is not DELEGATED protocol
        """
        if self.protocol() != Protocol.DELEGATED:
            raise ValueError("Can only get namespace for delegated addresses")
        namespace_bytes = self.payload()[: self.namespace_length]
        return leb128_decode(namespace_bytes)

    @property
    def sub_addr(self) -> bytes:
        """
        Get the sub-address bytes (DELEGATED addresses only).

        Returns:
            Sub-address bytes

        Raises:
            ValueError: If address is not DELEGATED protocol
        """
        if self.protocol() != Protocol.DELEGATED:
            raise ValueError("Can only get subaddress for delegated addresses")
        # Sub-address starts after protocol byte (1) + namespace bytes
        return self.bytes[1 + self.namespace_length :]

    @property
    def sub_addr_hex(self) -> str:
        """
        Get the sub-address as hex string (DELEGATED addresses only).

        Returns:
            Sub-address as hex string (without 0x prefix)
        """
        return self.sub_addr.hex()

    def to_string(self) -> str:
        """
        Convert address to string representation.

        Returns:
            Address string (e.g., "f1...", "t1...", "f410f...")
        """
        from .encoding import encode

        return encode(self._coin_type.value, self)

    def equals(self, addr: "Address") -> bool:
        """
        Check if this address equals another address.

        Args:
            addr: Address to compare

        Returns:
            True if addresses are equal, False otherwise
        """
        if self is addr:
            return True
        return self.bytes == addr.bytes

    def __str__(self) -> str:
        """String representation of address."""
        return self.to_string()

    def __repr__(self) -> str:
        """Representation of address."""
        return f"Address(bytes={self.bytes.hex()}, coin_type={self._coin_type.value})"

    def __eq__(self, other: object) -> bool:
        """Equality comparison."""
        if not isinstance(other, Address):
            return False
        return self.equals(other)

