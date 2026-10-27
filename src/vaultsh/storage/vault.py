"""Local encrypted-byte vault container with atomic file replacement.

The functions accept arbitrary bytes. They do not yet define a wallet schema or
manage private keys, and the on-disk format needs independent review before use
with real wallet material.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from vaultsh.crypto.encryption import decrypt_bytes, encrypt_bytes

MAX_VAULT_FILE_SIZE = 64 * 1024 * 1024


class VaultError(ValueError):
    """Raised when a vault file is invalid or exceeds supported limits."""


def write_vault(
    path: str | Path, plaintext: bytes, password: str, *, overwrite: bool = False
) -> None:
    """Encrypt and atomically write ``plaintext`` to ``path``.

    Existing files are protected by default. Set ``overwrite=True`` only when
    replacing a known vault is intentional.
    """
    if not isinstance(plaintext, bytes):
        raise TypeError("plaintext must be bytes")
    if len(plaintext) > MAX_VAULT_FILE_SIZE:
        raise VaultError("Vault payload is larger than the supported size limit")
    target = Path(path)
    encrypted = encrypt_bytes(plaintext, password)
    if len(encrypted) > MAX_VAULT_FILE_SIZE:
        raise VaultError("Encrypted vault is larger than the supported size limit")
    _atomic_write(target, encrypted, overwrite=overwrite)


def read_vault(path: str | Path, password: str) -> bytes:
    """Read and authenticate an encrypted vault file."""
    target = Path(path)
    try:
        if target.stat().st_size > MAX_VAULT_FILE_SIZE:
            raise VaultError("Vault file is larger than the supported size limit")
        encrypted = target.read_bytes()
    except OSError as exc:
        raise VaultError(f"Unable to read vault file: {exc}") from exc
    try:
        return decrypt_bytes(encrypted, password)
    except (TypeError, ValueError) as exc:
        raise VaultError("Unable to decrypt vault file (wrong password or invalid file)") from exc


def _atomic_write(target: Path, data: bytes, *, overwrite: bool) -> None:
    parent = target.parent
    try:
        parent.mkdir(parents=True, exist_ok=True)
        file_descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{target.name}.", suffix=".tmp", dir=parent
        )
        temporary_path = Path(temporary_name)
        try:
            if os.name != "nt":
                os.chmod(temporary_path, 0o600)
            with os.fdopen(file_descriptor, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            if overwrite:
                os.replace(temporary_path, target)
            else:
                # Hard-linking is atomic and fails if another process created the
                # destination after the initial existence check. The temporary
                # file is in the same directory/filesystem by construction.
                os.link(temporary_path, target)
                temporary_path.unlink()
            if os.name != "nt":
                os.chmod(target, 0o600)
            # Persist directory metadata where supported.
            if hasattr(os, "O_DIRECTORY"):
                directory_fd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY)
                try:
                    os.fsync(directory_fd)
                finally:
                    os.close(directory_fd)
        except Exception:
            try:
                os.close(file_descriptor)
            except OSError:
                pass
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
            raise
    except OSError as exc:
        raise VaultError(f"Unable to write vault file: {exc}") from exc
