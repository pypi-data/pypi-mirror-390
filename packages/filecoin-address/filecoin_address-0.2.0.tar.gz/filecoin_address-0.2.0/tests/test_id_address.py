"""Tests for ID address functions."""

import pytest

from filecoin_address import (
    CoinType,
    Protocol,
    decode,
    eth_address_from_id,
    id_from_address,
    id_from_eth_address,
    id_from_payload,
)


class TestIdFromAddress:
    """Test id_from_address function."""

    def test_extract_id_from_address(self):
        """Test extracting ID from ID address."""
        address = decode("f01035")
        id_value = id_from_address(address)
        assert id_value == 1035

    def test_extract_id_from_address_id_1(self):
        """Test extracting ID 1."""
        address = decode("f01")
        id_value = id_from_address(address)
        assert id_value == 1

    def test_extract_id_from_address_id_0(self):
        """Test extracting ID 0."""
        address = decode("f00")
        id_value = id_from_address(address)
        assert id_value == 0

    def test_extract_id_from_large_address(self):
        """Test extracting ID from large ID address."""
        address = decode("f0100000")
        id_value = id_from_address(address)
        assert id_value == 100000

    def test_extract_id_from_non_id_address_raises(self):
        """Test that extracting ID from non-ID address raises error."""
        address = decode("f1abjxfbp274xpdqcpuaykwkfb43omjotacm2p3za")
        with pytest.raises(ValueError, match="Cannot get ID from non ID address"):
            id_from_address(address)


class TestIdFromPayload:
    """Test id_from_payload function."""

    def test_extract_id_from_payload(self):
        """Test extracting ID from payload bytes."""
        from filecoin_address.leb128_utils import encode as leb128_encode

        payload = leb128_encode(1035)
        id_value = id_from_payload(payload)
        assert id_value == 1035

    def test_extract_id_from_payload_id_1(self):
        """Test extracting ID 1 from payload."""
        from filecoin_address.leb128_utils import encode as leb128_encode

        payload = leb128_encode(1)
        id_value = id_from_payload(payload)
        assert id_value == 1

    def test_extract_id_from_payload_id_0(self):
        """Test extracting ID 0 from payload."""
        from filecoin_address.leb128_utils import encode as leb128_encode

        payload = leb128_encode(0)
        id_value = id_from_payload(payload)
        assert id_value == 0


class TestEthAddressFromId:
    """Test eth_address_from_id function."""

    def test_convert_id_address_to_eth(self):
        """Test converting ID address to Ethereum ID mask address."""
        eth_addr = eth_address_from_id("f01035")
        assert eth_addr.lower().startswith("0xff")
        assert len(eth_addr) == 42  # 0x + 40 hex chars
        # Should have 0xFF prefix (case-insensitive)
        assert eth_addr[:4].lower() == "0xff"

    def test_convert_id_1_to_eth(self):
        """Test converting ID 1 to Ethereum."""
        eth_addr = eth_address_from_id("f01")
        assert eth_addr.lower() == "0xff00000000000000000000000000000000000001"

    def test_convert_id_0_to_eth(self):
        """Test converting ID 0 to Ethereum."""
        eth_addr = eth_address_from_id("f00")
        assert eth_addr.lower() == "0xff00000000000000000000000000000000000000"

    def test_convert_large_id_to_eth(self):
        """Test converting large ID to Ethereum."""
        eth_addr = eth_address_from_id("f0100000")
        # ID 100000 = 0x186A0
        assert eth_addr.lower() == "0xff000000000000000000000000000000000186a0"

    def test_convert_testnet_id_to_eth(self):
        """Test converting testnet ID address."""
        eth_addr = eth_address_from_id("t01")
        # Should work the same regardless of network
        assert eth_addr.lower().startswith("0xff")

    def test_round_trip_conversion(self):
        """Test round-trip conversion f0 -> ETH -> f0."""
        original = "f01035"
        eth_addr = eth_address_from_id(original)
        converted_back = id_from_eth_address(eth_addr)
        assert converted_back == original

    def test_round_trip_conversion_id_1(self):
        """Test round-trip conversion for ID 1."""
        original = "f01"
        eth_addr = eth_address_from_id(original)
        converted_back = id_from_eth_address(eth_addr)
        assert converted_back == original


class TestIdFromEthAddress:
    """Test id_from_eth_address function."""

    def test_convert_eth_id_mask_to_id_address(self):
        """Test converting Ethereum ID mask address to f0."""
        eth_addr = "0xFF0000000000000000000000000000000000040B"
        f0_addr = id_from_eth_address(eth_addr)
        assert f0_addr == "f01035"  # 0x40B = 1035

    def test_convert_eth_id_mask_id_1(self):
        """Test converting Ethereum ID mask for ID 1."""
        eth_addr = "0xFF00000000000000000000000000000000000001"
        f0_addr = id_from_eth_address(eth_addr)
        assert f0_addr == "f01"

    def test_convert_eth_id_mask_id_0(self):
        """Test converting Ethereum ID mask for ID 0."""
        eth_addr = "0xFF00000000000000000000000000000000000000"
        f0_addr = id_from_eth_address(eth_addr)
        assert f0_addr == "f00"

    def test_convert_eth_id_mask_with_checksum(self):
        """Test converting Ethereum ID mask address with checksum."""
        # Checksummed version
        eth_addr = "0xFF00000000000000000000000000000000000001"
        f0_addr = id_from_eth_address(eth_addr)
        assert f0_addr == "f01"

    def test_convert_eth_id_mask_testnet(self):
        """Test converting Ethereum ID mask to testnet address."""
        eth_addr = "0xFF00000000000000000000000000000000000001"
        f0_addr = id_from_eth_address(eth_addr, CoinType.TEST)
        assert f0_addr == "t01"

    def test_convert_invalid_eth_address_raises(self):
        """Test that converting invalid Ethereum address raises error."""
        with pytest.raises(ValueError, match="Cannot convert non-ID mask address"):
            id_from_eth_address("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb")

    def test_convert_regular_eth_address_raises(self):
        """Test that converting regular Ethereum address raises error."""
        with pytest.raises(ValueError, match="Cannot convert non-ID mask address"):
            id_from_eth_address("0x1fa4cd7c7b4f5b5f5f5f5f5f5f5f5f5f5f5f5f")

    def test_round_trip_conversion_eth_to_f0_to_eth(self):
        """Test round-trip conversion ETH -> f0 -> ETH."""
        original_eth = "0xFF0000000000000000000000000000000000040B"
        f0_addr = id_from_eth_address(original_eth)
        converted_back = eth_address_from_id(f0_addr)
        # Should match (case-insensitive for hex)
        assert original_eth.lower() == converted_back.lower()


class TestIdAddressIntegration:
    """Integration tests for ID address functions."""

    def test_full_workflow(self):
        """Test full workflow: create ID address, convert to ETH, convert back."""
        from filecoin_address.address_creation import new_id_address

        # Create ID address
        address = new_id_address(12345)
        id_str = address.to_string()

        # Convert to Ethereum
        eth_addr = eth_address_from_id(id_str)

        # Convert back
        f0_addr = id_from_eth_address(eth_addr)

        # Should match
        assert f0_addr == id_str

    def test_id_address_protocol(self):
        """Test that ID addresses have correct protocol."""
        address = decode("f01035")
        assert address.protocol() == Protocol.ID

    def test_id_address_payload_extraction(self):
        """Test extracting payload and getting ID from it."""
        address = decode("f01035")
        payload = address.payload()
        id_value = id_from_payload(payload)
        assert id_value == 1035
        assert id_value == id_from_address(address)

