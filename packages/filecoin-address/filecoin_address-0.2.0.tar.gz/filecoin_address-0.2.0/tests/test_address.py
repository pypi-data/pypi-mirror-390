"""Tests for Address class."""

import pytest

from filecoin_address import Address, CoinType, Protocol


class TestAddress:
    """Test Address class."""

    def test_address_creation(self):
        """Test creating address from bytes."""
        # Protocol 1 (SECP256K1) + 20-byte payload
        protocol_byte = bytes([1])
        payload = bytes([0] * 20)
        bytes_data = protocol_byte + payload
        address = Address(bytes_data)
        assert address.protocol() == Protocol.SECP256K1
        assert len(address.payload()) == 20

    def test_address_protocol(self):
        """Test getting address protocol."""
        address = Address(bytes([0]) + bytes([1, 2, 3]))
        assert address.protocol() == Protocol.ID

    def test_address_payload(self):
        """Test getting address payload."""
        payload = bytes([1, 2, 3, 4, 5])
        address = Address(bytes([1]) + payload)
        assert address.payload() == payload

    def test_address_coin_type(self):
        """Test address coin type."""
        address = Address(bytes([1]) + bytes([0] * 20), CoinType.TEST)
        assert address.coin_type() == CoinType.TEST
        assert address.network() == CoinType.TEST

    def test_delegated_namespace(self):
        """Test getting namespace from delegated address."""
        # Create delegated address: protocol 4, namespace 10 (LEB128), sub-addr
        # LEB128(4) = [4], LEB128(10) = [10], sub-addr = 20 bytes
        protocol_byte = bytes([4])
        namespace_byte = bytes([10])  # LEB128 encoding of 10
        sub_addr = bytes([0x1f, 0xa4, 0xcd] + [0] * 17)  # 20 bytes
        payload = namespace_byte + sub_addr
        bytes_data = protocol_byte + payload
        address = Address(bytes_data)
        assert address.protocol() == Protocol.DELEGATED
        assert address.namespace == 10
        assert address.sub_addr == sub_addr

    def test_delegated_sub_addr_hex(self):
        """Test getting sub-address as hex."""
        protocol_byte = bytes([4])
        namespace_byte = bytes([10])
        sub_addr = bytes([0x1f, 0xa4, 0xcd] + [0] * 17)
        payload = namespace_byte + sub_addr
        bytes_data = protocol_byte + payload
        address = Address(bytes_data)
        assert address.sub_addr_hex == sub_addr.hex()

    def test_delegated_properties_on_non_delegated(self):
        """Test that delegated properties raise on non-delegated addresses."""
        address = Address(bytes([1]) + bytes([0] * 20))
        with pytest.raises(ValueError, match="delegated"):
            _ = address.namespace
        with pytest.raises(ValueError, match="delegated"):
            _ = address.sub_addr

    def test_address_equals(self):
        """Test address equality."""
        bytes_data = bytes([1]) + bytes([0] * 20)
        addr1 = Address(bytes_data)
        addr2 = Address(bytes_data)
        assert addr1.equals(addr2)
        assert addr1 == addr2

    def test_address_not_equals(self):
        """Test address inequality."""
        addr1 = Address(bytes([1]) + bytes([0] * 20))
        addr2 = Address(bytes([1]) + bytes([1] * 20))
        assert not addr1.equals(addr2)
        assert addr1 != addr2

    def test_address_to_string(self):
        """Test address string conversion."""
        address = Address(bytes([1]) + bytes([0] * 20))
        addr_str = address.to_string()
        assert isinstance(addr_str, str)
        assert addr_str.startswith("f1")

    def test_address_invalid_bytes(self):
        """Test creating address with invalid bytes raises error."""
        with pytest.raises(ValueError, match="Missing bytes"):
            Address(bytes())

    def test_address_invalid_protocol(self):
        """Test creating address with invalid protocol raises error."""
        with pytest.raises(ValueError, match="Invalid protocol"):
            Address(bytes([99]) + bytes([0] * 20))

