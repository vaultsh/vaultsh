import json
from pathlib import Path

import pytest

from vaultsh.storage.vault import VaultError, write_vault
from vaultsh.storage.vault_document import (
    VaultDocumentError,
    create_vault_document,
    read_vault_document,
)


def test_create_and_read_vault_document(tmp_path: Path) -> None:
    path = tmp_path / "main.vault"
    created = create_vault_document(path, "unit-test-passphrase", label="Primary")

    loaded = read_vault_document(path, "unit-test-passphrase")
    assert loaded == created
    assert loaded.label == "Primary"
    assert loaded.schema_version == 2
    assert loaded.wallet_count == 0
    assert path.read_bytes() != b"Primary"


def test_short_password_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(VaultDocumentError, match="at least 12 characters"):
        create_vault_document(tmp_path / "short.vault", "too-short")


def test_create_refuses_to_overwrite_existing_file(tmp_path: Path) -> None:
    path = tmp_path / "existing.vault"
    path.write_bytes(b"keep this file")

    with pytest.raises(FileExistsError):
        create_vault_document(path, "unit-test-passphrase")
    assert path.read_bytes() == b"keep this file"


@pytest.mark.parametrize("label", ["", " leading", "trailing ", "line\nbreak", "x" * 81])
def test_label_validation(label: str, tmp_path: Path) -> None:
    with pytest.raises(VaultDocumentError):
        create_vault_document(tmp_path / "bad.vault", "unit-test-passphrase", label=label)


def test_wrong_password_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "main.vault"
    create_vault_document(path, "correct-password")

    with pytest.raises(VaultError):
        read_vault_document(path, "wrong-password")


def test_unsupported_schema_version_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "future.vault"
    payload = {
        "schema": "vaultsh.vault",
        "schema_version": 99,
        "vault_id": "9ed264b0-1d0e-4556-bb2d-1d1c44e15e6d",
        "label": "Future",
        "created_at": "2026-10-27T10:00:00+00:00",
        "wallets": [],
    }
    write_vault(path, json.dumps(payload).encode("utf-8"), "unit-test-passphrase")

    with pytest.raises(VaultDocumentError, match="Unsupported vault schema version"):
        read_vault_document(path, "unit-test-passphrase")


def test_nonempty_wallet_records_are_rejected(tmp_path: Path) -> None:
    payload = {
        "schema": "vaultsh.vault",
        "schema_version": 1,
        "vault_id": "9ed264b0-1d0e-4556-bb2d-1d1c44e15e6d",
        "label": "Unsupported records",
        "created_at": "2026-10-27T10:00:00+00:00",
        "wallets": [{"name": "not supported"}],
    }
    path = tmp_path / "with-records.vault"
    write_vault(path, json.dumps(payload).encode("utf-8"), "unit-test-passphrase")
    with pytest.raises(VaultDocumentError, match="Wallet records are not supported"):
        read_vault_document(path, "unit-test-passphrase")


def test_non_json_vault_payload_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "not-json.vault"
    write_vault(path, b"not json", "passphrase")
    with pytest.raises(VaultDocumentError, match="valid UTF-8 JSON"):
        read_vault_document(path, "passphrase")
