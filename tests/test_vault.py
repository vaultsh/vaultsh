from pathlib import Path

import pytest

from vaultsh.storage.backup import create_backup, restore_backup
from vaultsh.storage.vault import VaultError, read_vault, write_vault


def test_vault_round_trip(tmp_path: Path) -> None:
    target = tmp_path / "wallet.vault"
    plaintext = b"synthetic unit test content only"
    write_vault(target, plaintext, "test-passphrase")
    assert target.exists()
    assert target.read_bytes() != plaintext
    assert read_vault(target, "test-passphrase") == plaintext


def test_wrong_password_is_rejected(tmp_path: Path) -> None:
    target = tmp_path / "wallet.vault"
    write_vault(target, b"dummy data", "correct")
    with pytest.raises(VaultError, match="Unable to decrypt"):
        read_vault(target, "incorrect")


def test_backup_and_restore_preserve_encrypted_file(tmp_path: Path) -> None:
    source = tmp_path / "wallet.vault"
    backup = tmp_path / "wallet.vault.backup"
    restored = tmp_path / "restored.vault"
    write_vault(source, b"fixture", "test-passphrase")
    create_backup(source, backup)
    restore_backup(backup, restored)
    assert source.read_bytes() == backup.read_bytes() == restored.read_bytes()
    assert read_vault(restored, "test-passphrase") == b"fixture"


def test_backup_does_not_overwrite_by_default(tmp_path: Path) -> None:
    source = tmp_path / "source.vault"
    backup = tmp_path / "backup.vault"
    write_vault(source, b"fixture", "passphrase")
    backup.write_bytes(b"existing")
    with pytest.raises(VaultError, match="Unable to copy"):
        create_backup(source, backup)
    assert backup.read_bytes() == b"existing"
