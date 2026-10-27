"""Offline Bitcoin Mainnet wallet primitives for BIP-39 and BIP-84.

This module derives only the first native-SegWit receiving address. It does not
query a node, compute balances, construct transactions, sign, or broadcast.
The implementation delegates standardized BIP-39/BIP-32 primitives to embit.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass, field

NETWORK_NAME = "bitcoin-mainnet"
ACCOUNT_PATH = "m/84'/0'/0'"
FIRST_RECEIVE_PATH = "m/84'/0'/0'/0/0"


class BitcoinWalletError(ValueError):
    """Raised when Bitcoin wallet material is invalid or unavailable."""


@dataclass(frozen=True, slots=True)
class DerivedBitcoinWallet:
    """Derived public details plus the recovery phrase (hidden from repr)."""

    mnemonic: str = field(repr=False)
    address: str
    network: str = NETWORK_NAME
    derivation_path: str = FIRST_RECEIVE_PATH


def _load_embit():  # type: ignore[no-untyped-def]
    """Import the chain-specific library lazily so informational CLI commands work."""
    try:
        from embit import bip32, bip39, script
    except ImportError as exc:
        raise BitcoinWalletError(
            "Bitcoin wallet support requires embit. Install the project dependencies with "
            "`python -m pip install -e .` and retry."
        ) from exc
    return bip32, bip39, script


def generate_mnemonic() -> str:
    """Generate a 12-word English BIP-39 phrase from 128 bits of OS entropy."""
    _, bip39, _ = _load_embit()
    mnemonic = bip39.mnemonic_from_bytes(secrets.token_bytes(16))
    if not bip39.mnemonic_is_valid(mnemonic):
        raise BitcoinWalletError("Mnemonic generation failed validation")
    return mnemonic


def normalize_mnemonic(mnemonic: str) -> str:
    """Normalize spacing and validate an English BIP-39 recovery phrase.

    This initial release supports 12- or 24-word English phrases and the empty
    BIP-39 passphrase only. It deliberately does not silently accept an
    additional passphrase that could derive an entirely different wallet.
    """
    if not isinstance(mnemonic, str):
        raise BitcoinWalletError("Recovery phrase must be text")
    if len(mnemonic) > 512:
        raise BitcoinWalletError("Recovery phrase is too long")
    normalized = " ".join(mnemonic.strip().split())
    if not normalized or any(ord(char) < 32 or ord(char) == 127 for char in normalized):
        raise BitcoinWalletError("Recovery phrase is invalid")
    if len(normalized.split()) not in (12, 24):
        raise BitcoinWalletError("Only 12- or 24-word recovery phrases are supported")
    _, bip39, _ = _load_embit()
    try:
        valid = bip39.mnemonic_is_valid(normalized)
    except (ValueError, TypeError):
        valid = False
    if not valid:
        raise BitcoinWalletError(
            "Invalid BIP-39 English recovery phrase or checksum; no wallet was changed"
        )
    return normalized


def derive_first_receive_address(mnemonic: str) -> DerivedBitcoinWallet:
    """Derive the BIP-84 Bitcoin Mainnet address at ``m/84'/0'/0'/0/0``."""
    normalized = normalize_mnemonic(mnemonic)
    bip32, bip39, script = _load_embit()
    try:
        seed = bip39.mnemonic_to_seed(normalized)
        root_key = bip32.HDKey.from_seed(seed)
        account_key = root_key.derive(ACCOUNT_PATH)
        first_receive_key = account_key.to_public().derive([0, 0]).key
        address = script.p2wpkh(first_receive_key).address()
    except Exception as exc:
        # Avoid passing library exception text through the CLI; it may contain
        # implementation details or unexpected input fragments.
        raise BitcoinWalletError("Could not derive the Bitcoin receiving address") from exc
    if not isinstance(address, str) or not address.startswith("bc1q") or len(address) != 42:
        raise BitcoinWalletError(
            "Derived address did not match the expected Bitcoin Mainnet format"
        )
    return DerivedBitcoinWallet(mnemonic=normalized, address=address)
