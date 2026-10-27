"""Minimal protocol shared by chain-specific network adapters."""

from typing import Protocol


class NetworkError(RuntimeError):
    """Raised when a chain adapter cannot complete a network operation."""


class NetworkAdapter(Protocol):
    """Minimum read-only interface expected from an adapter.

    Implementations must use chain-specific validation rules. A shared protocol
    does not imply shared address formats, derivation, signing, or transactions.
    """

    @property
    def network_name(self) -> str:
        """Return a stable network identifier, for example ``bitcoin-mainnet``."""
        ...

    def validate_address(self, address: str) -> bool:
        """Validate a public address using the rules of this network."""
        ...
