"""Encrypted wallet-store tests use a deterministic fake derivation when testing storage."""

import json
from pathlib import Path
from typing import Any

import pytest

from vaultsh.networks.bitcoin.wallet import DerivedBitcoinWallet
from vaultsh.storage.vault import write_vault
from vaultsh.storage.vault_document import create_vault_document, read_vault_document
from vaultsh.storage.wallet_store import (
    WalletStoreError,
    add_bitcoin_wallet,
    get_recovery_phrase,
    list_wallets,
)

PASSWORD = "test-only-password-phrase"
MNEMONIC = (
    "abandon abandon abandon abandon abandon abandon "
    "abandon abandon abandon abandon abandon about"
)
ADDRESS = "bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu"


def _fake_derivation(_: str) -> DerivedBitcoinWallet:
    return DerivedBitcoinWallet(mnemonic=MNEMONIC, address=ADDRESS)


def _legacy_v1_payload() -> dict[str, Any]:
    return {
        "schema": "vaultsh.vault",
        "schema_version": 1,
        "vault_id": "9ed264b0-1d0e-4556-bb2d-1d1c44e15e6d",
        "label": "Legacy vault",
        "created_at": "2026-10-27T10:00:00+00:00",
        "wallets": [],
    }


def test_add_wallet_stores_phrase_only_inside_encrypted_container(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import vaultsh.storage.wallet_store as wallet_store

    monkeypatch.setattr(wallet_store, "derive_first_receive_address", _fake_derivation)
    path = tmp_path / "main.vault"
    create_vault_document(path, PASSWORD, label="Main")

    summary = add_bitcoin_wallet(path, PASSWORD, label="Savings", mnemonic=MNEMONIC)
    assert summary.address == ADDRESS
    assert summary.network == "bitcoin-mainnet"
    assert summary.derivation_path == "m/84'/0'/0'/0/0"

    public_document = read_vault_document(path, PASSWORD)
    assert public_document.schema_version == 2
    assert public_document.wallet_count == 1
    assert MNEMONIC.encode() not in path.read_bytes()

    records = list_wallets(path, PASSWORD)
    assert len(records) == 1
    assert records[0].label == "Savings"
    assert MNEMONIC not in repr(records)
    assert get_recovery_phrase(path, PASSWORD, summary.wallet_id) == MNEMONIC


def test_duplicate_wallet_address_is_rejected_without_changing_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import vaultsh.storage.wallet_store as wallet_store

    monkeypatch.setattr(wallet_store, "derive_first_receive_address", _fake_derivation)
    path = tmp_path / "main.vault"
    create_vault_document(path, PASSWORD, label="Main")
    add_bitcoin_wallet(path, PASSWORD, label="Savings", mnemonic=MNEMONIC)
    before = path.read_bytes()

    with pytest.raises(WalletStoreError, match="already present"):
        add_bitcoin_wallet(path, PASSWORD, label="Duplicate", mnemonic=MNEMONIC)
    assert path.read_bytes() == before


def test_adding_wallet_migrates_schema_v1_to_v2(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import vaultsh.storage.wallet_store as wallet_store

    monkeypatch.setattr(wallet_store, "derive_first_receive_address", _fake_derivation)
    path = tmp_path / "legacy.vault"
    write_vault(path, json.dumps(_legacy_v1_payload()).encode(), PASSWORD)
    assert read_vault_document(path, PASSWORD).schema_version == 1

    add_bitcoin_wallet(path, PASSWORD, label="Imported", mnemonic=MNEMONIC)
    migrated = read_vault_document(path, PASSWORD)
    assert migrated.schema_version == 2
    assert migrated.wallet_count == 1


def test_wrong_password_does_not_modify_wallet_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import vaultsh.storage.wallet_store as wallet_store

    monkeypatch.setattr(wallet_store, "derive_first_receive_address", _fake_derivation)
    path = tmp_path / "main.vault"
    create_vault_document(path, PASSWORD)
    before = path.read_bytes()
    with pytest.raises(ValueError):
        add_bitcoin_wallet(path, "incorrect-password-value", label="Savings", mnemonic=MNEMONIC)
    assert path.read_bytes() == before


def test_unknown_wallet_id_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "main.vault"
    create_vault_document(path, PASSWORD)
    with pytest.raises(WalletStoreError, match="not found"):
        get_recovery_phrase(path, PASSWORD, "9ed264b0-1d0e-4556-bb2d-1d1c44e15e6d")


def test_invalid_wallet_record_is_rejected_by_schema(tmp_path: Path) -> None:
    from vaultsh.storage.vault_document import VaultDocumentError, _write_payload

    path = tmp_path / "invalid.vault"
    payload = {
        "schema": "vaultsh.vault",
        "schema_version": 2,
        "vault_id": "9ed264b0-1d0e-4556-bb2d-1d1c44e15e6d",
        "label": "Main",
        "created_at": "2026-10-27T10:00:00+00:00",
        "wallets": [{"wallet_id": "bad", "mnemonic": MNEMONIC}],
    }
    with pytest.raises(VaultDocumentError, match="missing or unexpected fields"):
        _write_payload(path, PASSWORD, payload, overwrite=False)
