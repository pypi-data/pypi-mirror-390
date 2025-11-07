"""Tests for encoding and decoding functions."""

import pytest

from filecoin_address import CoinType, decode, encode, new_from_string


class TestDecode:
    """Test decode function."""

    def test_decode_secp256k1_address(self):
        """Test decoding SECP256K1 address."""
        address_str = "f1lp74mm3dw4daywmsgbhk33sis4xfvnzr7knavbq"
        address = decode(address_str)
        assert address.protocol().value == 1
        assert address.coin_type() == CoinType.MAIN

    def test_decode_id_address(self):
        """Test decoding ID address."""
        address_str = "f01"
        address = decode(address_str)
        assert address.protocol().value == 0

    def test_decode_delegated_address(self):
        """Test decoding delegated address."""
        address_str = "t410fguptud5pzd7zpvjvt54tuds5kidntoyn3oivr6y"
        address = decode(address_str)
        assert address.protocol().value == 4
        assert address.namespace == 10

    def test_decode_invalid_address(self):
        """Test decoding invalid address raises error."""
        with pytest.raises(ValueError):
            decode("invalid")


class TestEncode:
    """Test encode function."""

    def test_encode_address(self):
        """Test encoding address to string."""
        from filecoin_address import Address

        bytes_data = bytes([1]) + bytes([0] * 20)
        address = Address(bytes_data)
        encoded = encode("f", address)
        assert isinstance(encoded, str)
        assert encoded.startswith("f1")

    def test_encode_id_address(self):
        """Test encoding ID address."""
        from filecoin_address.address_creation import new_id_address

        address = new_id_address(1)
        encoded = encode("f", address)
        assert encoded == "f01"

    def test_encode_testnet(self):
        """Test encoding testnet address."""
        from filecoin_address import Address

        bytes_data = bytes([1]) + bytes([0] * 20)
        address = Address(bytes_data, CoinType.TEST)
        encoded = encode("t", address)
        assert encoded.startswith("t1")


class TestNewFromString:
    """Test new_from_string function."""

    def test_new_from_string(self):
        """Test creating address from string."""
        from filecoin_address import Address

        address_str = "f1abjxfbp274xpdqcpuaykwkfb43omjotacm2p3za"
        address = new_from_string(address_str)
        assert isinstance(address, Address)
        assert address.to_string() == address_str

