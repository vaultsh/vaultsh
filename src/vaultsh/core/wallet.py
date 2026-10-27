"""Non-secret wallet metadata models.

This module intentionally does not create keys, mnemonics, or blockchain
addresses. Those operations require chain-specific implementations and review.
"""

from dataclasses import dataclass
import re

_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")


@dataclass(frozen=True, slots=True)
class WalletSummary:
    """Validated metadata safe to display in ordinary UI elements."""

    wallet_id: str
    network: str
    label: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.wallet_id, str) or not _IDENTIFIER.fullmatch(self.wallet_id):
            raise ValueError("wallet_id must be 1-64 safe identifier characters")
        if not isinstance(self.network, str) or not _IDENTIFIER.fullmatch(self.network):
            raise ValueError("network must be 1-64 safe identifier characters")
        if not isinstance(self.label, str):
            raise ValueError("label must be a string")
        if len(self.label) > 80:
            raise ValueError("label must be 80 characters or fewer")
        if any(ord(char) < 32 or ord(char) == 127 for char in self.label):
            raise ValueError("label must not contain control characters")
