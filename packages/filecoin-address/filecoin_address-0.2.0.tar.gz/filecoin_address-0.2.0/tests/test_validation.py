"""Tests for address validation functions."""

import pytest

from filecoin_address import validate_address_string, check_address_string


class TestValidateAddressString:
    """Test validate_address_string function."""

    def test_valid_secp256k1_address(self):
        """Test validation of valid SECP256K1 address."""
        # Example valid address
        address = "f1abjxfbp274xpdqcpuaykwkfb43omjotacm2p3za"
        assert validate_address_string(address) is True

    def test_valid_id_address(self):
        """Test validation of valid ID address."""
        address = "f01"
        assert validate_address_string(address) is True

    def test_valid_delegated_address(self):
        """Test validation of valid delegated address."""
        address = "f410fguptud5pzd7zpvjvt54tuds5kidntoyn3oivr6y"
        assert validate_address_string(address) is True

    def test_invalid_address_too_short(self):
        """Test validation rejects address that's too short."""
        assert validate_address_string("f1") is False

    def test_invalid_address_bad_coin_type(self):
        """Test validation rejects address with bad coin type."""
        assert validate_address_string("x1abjxfbp274xpdqcpuaykwkfb43omjotacm2p3za") is False

    def test_invalid_address_bad_protocol(self):
        """Test validation rejects address with bad protocol."""
        assert validate_address_string("f9abjxfbp274xpdqcpuaykwkfb43omjotacm2p3za") is False

    def test_invalid_address_bad_checksum(self):
        """Test validation rejects address with bad checksum."""
        # Valid format but wrong checksum
        address = "f1abjxfbp274xpdqcpuaykwkfb43omjotacm2p3zz"
        assert validate_address_string(address) is False


class TestCheckAddressString:
    """Test check_address_string function."""

    def test_check_valid_secp256k1_address(self):
        """Test checking valid SECP256K1 address."""
        address = "f1abjxfbp274xpdqcpuaykwkfb43omjotacm2p3za"
        result = check_address_string(address)
        assert result["protocol"] == 1
        assert result["coinType"] == "f"
        assert isinstance(result["payload"], bytes)
        assert isinstance(result["bytes"], bytes)

    def test_check_valid_id_address(self):
        """Test checking valid ID address."""
        address = "f01"
        result = check_address_string(address)
        assert result["protocol"] == 0
        assert result["coinType"] == "f"
        assert isinstance(result["payload"], bytes)

    def test_check_valid_delegated_address(self):
        """Test checking valid delegated address."""
        address = "f410fguptud5pzd7zpvjvt54tuds5kidntoyn3oivr6y"
        result = check_address_string(address)
        assert result["protocol"] == 4
        assert result["coinType"] == "f"
        assert result["namespace"] == 10
        assert isinstance(result["payload"], bytes)

    def test_check_invalid_address_raises(self):
        """Test checking invalid address raises ValueError."""
        with pytest.raises(ValueError):
            check_address_string("invalid")

    def test_check_testnet_address(self):
        """Test checking testnet address."""
        address = "t1abjxfbp274xpdqcpuaykwkfb43omjotacm2p3za"
        result = check_address_string(address)
        assert result["coinType"] == "t"

