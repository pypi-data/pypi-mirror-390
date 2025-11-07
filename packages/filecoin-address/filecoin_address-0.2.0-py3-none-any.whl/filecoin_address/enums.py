"""Enums for Filecoin address protocols and types."""

from enum import Enum


class Protocol(int, Enum):
    """Filecoin address protocol types."""

    ID = 0
    SECP256K1 = 1
    ACTOR = 2
    BLS = 3
    DELEGATED = 4


class DelegatedNamespace(int, Enum):
    """Delegated address namespace types."""

    EVM = 10


class CoinType(str, Enum):
    """Filecoin network coin types."""

    MAIN = "f"
    TEST = "t"

