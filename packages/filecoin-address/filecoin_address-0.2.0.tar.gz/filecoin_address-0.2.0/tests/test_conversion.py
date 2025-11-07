"""Tests for address conversion functions."""

import pytest

from filecoin_address import (
    CoinType,
    delegated_from_eth_address,
    eth_address_from_delegated,
)


class TestDelegatedFromEthAddress:
    """Test delegated_from_eth_address function."""

    def test_convert_valid_eth_address(self):
        """Test converting valid Ethereum address to f410."""
        eth_addr = "0x351F3A0FAfc8fF97d5359f793A0e5d5206D9BB0D"
        result = delegated_from_eth_address(eth_addr)
        assert result.startswith("f410f")
        assert len(result) > 10

    def test_convert_eth_address_testnet(self):
        """Test converting Ethereum address to testnet f410."""
        eth_addr = "0x351F3A0FAfc8fF97d5359f793A0e5d5206D9BB0D"
        result = delegated_from_eth_address(eth_addr, CoinType.TEST)
        assert result.startswith("t410f")

    def test_convert_invalid_eth_address(self):
        """Test converting invalid Ethereum address raises error."""
        with pytest.raises(ValueError, match="Invalid Ethereum address"):
            delegated_from_eth_address("0xinvalid")

    def test_convert_zero_address(self):
        """Test converting zero address raises error."""
        with pytest.raises(ValueError, match="Invalid Ethereum address"):
            delegated_from_eth_address("0x0000000000000000000000000000000000000000")

    def test_round_trip_conversion(self):
        """Test round-trip conversion ETH -> f410 -> ETH."""
        eth_addr = "0x351F3A0FAfc8fF97d5359f793A0e5d5206D9BB0D"
        f410_addr = delegated_from_eth_address(eth_addr)
        converted_back = eth_address_from_delegated(f410_addr)
        # Should match (case-insensitive for hex)
        assert f410_addr.lower() == "f410fguptud5pzd7zpvjvt54tuds5kidntoyn3oivr6y"
        assert eth_addr.lower() == converted_back.lower()


class TestEthAddressFromDelegated:
    """Test eth_address_from_delegated function."""

    def test_convert_valid_delegated_address(self):
        """Test converting valid f410 address to Ethereum address."""
        f410_addr = "t410fguptud5pzd7zpvjvt54tuds5kidntoyn3oivr6y"
        result = eth_address_from_delegated(f410_addr)
        assert result.startswith("0x")
        assert len(result) == 42  # 0x + 40 hex chars

    def test_convert_invalid_delegated_address(self):
        """Test converting invalid delegated address raises error."""
        with pytest.raises(ValueError):
            eth_address_from_delegated("f1abjxfbp274xpdqcpuaykwkfb43omjotacm2p3za")

    def test_convert_non_delegated_address(self):
        """Test converting non-delegated address raises error."""
        with pytest.raises(ValueError, match="not a delegated address"):
            eth_address_from_delegated("f01")

    def test_convert_wrong_namespace(self):
        """Test converting delegated address with wrong namespace raises error."""
        # This would need a test address with namespace != 10
        # For now, we'll test that the function validates namespace
        pass  # TODO: Add test with actual wrong namespace address if available

