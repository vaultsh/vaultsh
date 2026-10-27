"""Storage operations for chain-specific wallet records inside encrypted vaults."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from vaultsh.core.wallet import WalletSummary
from vaultsh.networks.bitcoin.wallet import derive_first_receive_address
from vaultsh.storage.vault_document import (
    VAULT_SCHEMA_VERSION,
    VaultDocumentError,
    _read_payload,
    _write_payload,
)


class WalletStoreError(ValueError):
    """Raised when a wallet record cannot be safely stored or retrieved."""


def add_bitcoin_wallet(
    path: str | Path, password: str, *, label: str, mnemonic: str
) -> WalletSummary:
    """Derive and store a Bitcoin wallet, keeping its phrase inside the encrypted vault."""
    if not isinstance(label, str) or not label or label.strip() != label or len(label) > 80:
        raise WalletStoreError("Wallet label must be 1-80 characters without outer spaces")
    if any(ord(char) < 32 or ord(char) == 127 for char in label):
        raise WalletStoreError("Wallet label must not contain control characters")

    derived = derive_first_receive_address(mnemonic)
    payload = _read_payload(path, password)
    wallets: list[dict[str, Any]] = payload["wallets"]
    if any(record["address"] == derived.address for record in wallets):
        raise WalletStoreError("This Bitcoin wallet is already present in the vault")

    wallet_id = str(uuid.uuid4())
    created_at = datetime.now(UTC).isoformat(timespec="seconds")
    record: dict[str, Any] = {
        "wallet_id": wallet_id,
        "label": label,
        "network": derived.network,
        "address": derived.address,
        "derivation_path": derived.derivation_path,
        "created_at": created_at,
        "mnemonic": derived.mnemonic,
    }
    # Schema-v1 vaults are migrated in-place only after the complete new
    # document validates and is ready for an atomic encrypted replacement.
    payload["schema_version"] = VAULT_SCHEMA_VERSION
    wallets.append(record)
    try:
        _write_payload(path, password, payload, overwrite=True)
    except (OSError, ValueError) as exc:
        raise WalletStoreError("Unable to save wallet into the encrypted vault") from exc
    return _summary(record)


def list_wallets(path: str | Path, password: str) -> tuple[WalletSummary, ...]:
    """Return only public metadata; recovery phrases are never included in results."""
    payload = _read_payload(path, password)
    return tuple(_summary(record) for record in payload["wallets"])


def get_recovery_phrase(path: str | Path, password: str, wallet_id: str) -> str:
    """Return a phrase only to an explicit CLI action that has unlocked the vault."""
    if not isinstance(wallet_id, str):
        raise WalletStoreError("Wallet ID must be a string")
    try:
        canonical_id = str(uuid.UUID(wallet_id))
    except (ValueError, AttributeError) as exc:
        raise WalletStoreError("Wallet ID is invalid") from exc
    payload = _read_payload(path, password)
    for record in payload["wallets"]:
        if record["wallet_id"] == canonical_id:
            return record["mnemonic"]
    raise WalletStoreError("Wallet ID was not found in this vault")


def _summary(record: dict[str, Any]) -> WalletSummary:
    return WalletSummary(
        wallet_id=record["wallet_id"],
        network=record["network"],
        label=record["label"],
        address=record["address"],
        derivation_path=record["derivation_path"],
        created_at=record["created_at"],
    )
