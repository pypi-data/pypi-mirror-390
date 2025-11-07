# filecoin-address-python

Filecoin address manipulation routines for Python. This library provides utilities for working with Filecoin addresses, including validation, encoding, decoding, and conversion between native Filecoin addresses and EVM delegated addresses.

## Installation

```bash
pip install filecoin-address
```

## Usage

### Validation

Validate Filecoin address strings:

```python
from filecoin_address import validate_address_string, check_address_string

# Simple validation (returns True/False)
is_valid = validate_address_string("f1abjxfbp274xpdqcpuaykwkfb43omjotacm2p3za")
print(is_valid)  # True

# Detailed validation (returns address data or raises ValueError)
address_data = check_address_string("f1abjxfbp274xpdqcpuaykwkfb43omjotacm2p3za")
print(address_data["protocol"])  # 1 (SECP256K1)
print(address_data["coinType"])   # "f" (mainnet)
```

### Conversion Between Ethereum and Filecoin Addresses

Convert between Ethereum addresses (0x...) and Filecoin delegated addresses (f410...):

```python
from filecoin_address import (
    delegated_from_eth_address,
    eth_address_from_delegated,
    CoinType,
)

# Convert Ethereum address to Filecoin delegated address
eth_addr = "0x351F3A0FAfc8fF97d5359f793A0e5d5206D9BB0D"
f410_addr = delegated_from_eth_address(eth_addr)
print(f410_addr)  # "f410f..."

# Convert Filecoin delegated address to Ethereum address
converted_back = eth_address_from_delegated(f410_addr)
print(converted_back)  # "0x1fa4cd7c7b4f5b5f5f5f5f5f5f5f5f5f5f5f" (with checksum)

# Use testnet
t410_addr = delegated_from_eth_address(eth_addr, CoinType.TEST)
print(t410_addr)  # "t410f..."
```

### Encoding and Decoding

```python
from filecoin_address import decode, encode, new_from_string, Address

# Decode address string to Address object
address = decode("f1abjxfbp274xpdqcpuaykwkfb43omjotacm2p3za")
print(address.protocol())  # Protocol.SECP256K1
print(address.payload())   # bytes

# Encode Address object to string
address_str = encode("f", address)
print(address_str)

# Convenience function
address = new_from_string("f1abjxfbp274xpdqcpuaykwkfb43omjotacm2p3za")
```

### Working with Address Objects

```python
from filecoin_address import Address, Protocol, CoinType

# Create address from bytes
bytes_data = bytes([1]) + bytes([0] * 20)  # Protocol 1 + 20-byte payload
address = Address(bytes_data, CoinType.MAIN)

# Access address properties
print(address.protocol())    # Protocol.SECP256K1
print(address.payload())     # bytes
print(address.coin_type())   # CoinType.MAIN
print(address.to_string())   # "f1..."

# For delegated addresses
if address.protocol() == Protocol.DELEGATED:
    print(address.namespace)      # namespace number
    print(address.sub_addr)       # sub-address bytes
    print(address.sub_addr_hex)   # sub-address as hex string
```

### Address Types

The library supports all Filecoin address protocols:

- **ID** (0): Numeric ID addresses (e.g., `f01`, `f02`)
- **SECP256K1** (1): Secp256k1 public key addresses
- **ACTOR** (2): Actor addresses
- **BLS** (3): BLS public key addresses
- **DELEGATED** (4): Delegated addresses (e.g., `f410f...` for EVM)

### Network Types

- **MAIN** (`"f"`): Mainnet addresses
- **TEST** (`"t"`): Testnet addresses

## API Reference

### Validation Functions

- `validate_address_string(address: str) -> bool`: Validate address string format and checksum
- `check_address_string(address: str) -> dict`: Validate and parse address, returns address data

### Conversion Functions

- `delegated_from_eth_address(eth_addr: str, coin_type: CoinType = CoinType.MAIN) -> str`: Convert Ethereum address to f410 delegated address
- `eth_address_from_delegated(delegated: str) -> str`: Convert f410 delegated address to Ethereum address

### Encoding Functions

- `decode(address: str) -> Address`: Decode address string to Address object
- `encode(coin_type: str, address: Address) -> str`: Encode Address object to string
- `new_from_string(address: str) -> Address`: Create Address from string (convenience function)

### Address Class

- `Address(bytes_data: bytes, coin_type: CoinType = CoinType.MAIN)`: Create address from bytes
- `protocol() -> Protocol`: Get address protocol
- `payload() -> bytes`: Get address payload
- `coin_type() -> CoinType`: Get network coin type
- `to_string() -> str`: Convert to address string
- `equals(addr: Address) -> bool`: Compare addresses

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/glifio/filecoin-address-python.git
cd filecoin-address-python

# Install dependencies
pip install -r requirements-dev.txt

# Install package in development mode
pip install -e .
```

### Running Tests

```bash
pytest
```

### Packaged example

There is a simple exampel to show how to use the module from your own external code.

To run it, install the module then try:

```bash
cd examples
python ./convert_address.py 0x351F3A0FAfc8fF97d5359f793A0e5d5206D9BB0D
```

## License

This repository is dual-licensed under Apache 2.0 and MIT terms.

## Credits

This library is a Python translation of [@glif/filecoin-address](https://github.com/glifio/modules/tree/primary/packages/filecoin-address), inspired by [go-address](https://github.com/filecoin-project/go-address).
