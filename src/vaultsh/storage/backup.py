"""Atomic backup and restore helpers for already-encrypted vault files.

These functions copy bytes without decrypting them. Backups remain sensitive
because encryption strength depends on the user's password and device security.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from vaultsh.crypto.encryption import MAGIC
from vaultsh.storage.vault import MAX_VAULT_FILE_SIZE, VaultError


def create_backup(
    vault_path: str | Path, backup_path: str | Path, *, overwrite: bool = False
) -> Path:
    """Copy an encrypted vault to a backup file and return its path."""
    return _copy_encrypted_file(Path(vault_path), Path(backup_path), overwrite=overwrite)


def restore_backup(
    backup_path: str | Path, vault_path: str | Path, *, overwrite: bool = False
) -> Path:
    """Restore a byte-for-byte encrypted backup to a vault path."""
    return _copy_encrypted_file(Path(backup_path), Path(vault_path), overwrite=overwrite)


def _copy_encrypted_file(source: Path, destination: Path, *, overwrite: bool) -> Path:
    try:
        if source.resolve() == destination.resolve():
            raise VaultError("Source and destination must be different files")
        if not source.is_file():
            raise VaultError("Backup source is not a regular file")
        if source.stat().st_size > MAX_VAULT_FILE_SIZE:
            raise VaultError("Source file is larger than the supported size limit")
        if destination.exists() and not overwrite:
            raise FileExistsError(destination)
        data = source.read_bytes()
        if not data.startswith(MAGIC):
            raise VaultError("Source does not look like a Vaultsh encrypted file")
        destination.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
        )
        temporary = Path(temporary_name)
        try:
            if os.name != "nt":
                os.chmod(temporary, 0o600)
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            # Re-check to avoid replacing a file if overwrite was not authorized.
            if destination.exists() and not overwrite:
                raise FileExistsError(destination)
            if overwrite:
                os.replace(temporary, destination)
            else:
                # Atomic no-clobber operation; unlike exists()+replace(), this
                # also protects against a destination appearing during the copy.
                os.link(temporary, destination)
                temporary.unlink()
            if os.name != "nt":
                os.chmod(destination, 0o600)
            return destination
        except Exception:
            try:
                os.close(descriptor)
            except OSError:
                pass
            temporary.unlink(missing_ok=True)
            raise
    except OSError as exc:
        raise VaultError(f"Unable to copy encrypted file: {exc}") from exc
