"""Versioned document schema stored inside an encrypted Vaultsh container.

Schema v1 containers contained metadata and an empty wallet list. Schema v2
supports Bitcoin Mainnet wallet records whose recovery phrases are protected by
the enclosing authenticated encrypted file. Readers remain compatible with v1.
"""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from vaultsh.storage.vault import read_vault, write_vault

VAULT_SCHEMA = "vaultsh.vault"
VAULT_SCHEMA_VERSION = 2
SUPPORTED_VAULT_SCHEMA_VERSIONS = (1, 2)
MAX_LABEL_LENGTH = 80
MIN_VAULT_PASSWORD_LENGTH = 12
_WALLET_ID = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")
_MNEMONIC = re.compile(r"(?:[a-z]+(?: [a-z]+){11}|[a-z]+(?: [a-z]+){23})\Z")
_RECEIVE_PATH = "m/84'/0'/0'/0/0"


class VaultDocumentError(ValueError):
    """Raised when vault metadata is malformed or uses an unsupported schema."""


@dataclass(frozen=True, slots=True)
class VaultDocument:
    """Public metadata for a local encrypted container."""

    vault_id: str
    label: str
    created_at: str
    schema_version: int = VAULT_SCHEMA_VERSION
    wallet_count: int = 0


def create_vault_document(
    path: str | Path, password: str, *, label: str = "My Vault"
) -> VaultDocument:
    """Create a new encrypted schema-v2 container with no wallet records."""
    _validate_label(label)
    _validate_new_password(password)
    target = Path(path)
    if target.exists():
        raise FileExistsError(target)

    created_at = datetime.now(UTC).isoformat(timespec="seconds")
    vault_id = str(uuid.uuid4())
    payload: dict[str, Any] = {
        "schema": VAULT_SCHEMA,
        "schema_version": VAULT_SCHEMA_VERSION,
        "vault_id": vault_id,
        "label": label,
        "created_at": created_at,
        "wallets": [],
    }
    _write_payload(target, password, payload, overwrite=False)
    return VaultDocument(vault_id, label, created_at, VAULT_SCHEMA_VERSION, 0)


def read_vault_document(path: str | Path, password: str) -> VaultDocument:
    """Decrypt and validate metadata without returning any recovery material."""
    payload = _read_payload(path, password)
    return _public_document(payload)


def _read_payload(path: str | Path, password: str) -> dict[str, Any]:
    """Internal helper used by storage operations that must handle wallet secrets."""
    raw = read_vault(path, password)
    try:
        payload: Any = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VaultDocumentError("Vault payload is not valid UTF-8 JSON") from exc
    _validate_payload(payload)
    return payload


def _write_payload(
    path: str | Path, password: str, payload: dict[str, Any], *, overwrite: bool
) -> None:
    """Validate and encrypt a document before an atomic write."""
    _validate_payload(payload)
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    write_vault(path, raw, password, overwrite=overwrite)


def _public_document(payload: dict[str, Any]) -> VaultDocument:
    return VaultDocument(
        vault_id=payload["vault_id"],
        label=payload["label"],
        created_at=payload["created_at"],
        schema_version=payload["schema_version"],
        wallet_count=len(payload["wallets"]),
    )


def _validate_payload(payload: Any) -> None:
    if not isinstance(payload, dict):
        raise VaultDocumentError("Vault payload must be a JSON object")
    expected_fields = {
        "schema", "schema_version", "vault_id", "label", "created_at", "wallets"
    }
    actual_fields = set(payload)
    if actual_fields != expected_fields:
        missing = sorted(expected_fields - actual_fields)
        unknown = sorted(actual_fields - expected_fields)
        details = []
        if missing:
            details.append(f"missing fields: {', '.join(missing)}")
        if unknown:
            details.append(f"unknown fields: {', '.join(unknown)}")
        raise VaultDocumentError("Invalid vault document fields (" + "; ".join(details) + ")")
    if payload.get("schema") != VAULT_SCHEMA:
        raise VaultDocumentError("Unrecognized Vaultsh document schema")

    version = payload.get("schema_version")
    if isinstance(version, bool) or not isinstance(version, int):
        raise VaultDocumentError("schema_version must be an integer")
    if version not in SUPPORTED_VAULT_SCHEMA_VERSIONS:
        raise VaultDocumentError(f"Unsupported vault schema version: {version}")

    vault_id = payload.get("vault_id")
    if not isinstance(vault_id, str):
        raise VaultDocumentError("vault_id must be a UUID string")
    try:
        parsed_id = uuid.UUID(vault_id)
    except (ValueError, AttributeError) as exc:
        raise VaultDocumentError("vault_id must be a UUID string") from exc
    if str(parsed_id) != vault_id:
        raise VaultDocumentError("vault_id must use canonical lowercase UUID syntax")

    _validate_label(payload.get("label"))
    created_at = payload.get("created_at")
    if not isinstance(created_at, str):
        raise VaultDocumentError("created_at must be an ISO 8601 timestamp")
    try:
        timestamp = datetime.fromisoformat(created_at)
    except ValueError as exc:
        raise VaultDocumentError("created_at must be an ISO 8601 timestamp") from exc
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise VaultDocumentError("created_at must include a timezone")

    wallets = payload.get("wallets")
    if not isinstance(wallets, list):
        raise VaultDocumentError("wallets must be a list")
    if version == 1 and wallets:
        raise VaultDocumentError("Wallet records are not supported by schema version 1")
    if version == 2:
        seen_ids: set[str] = set()
        seen_addresses: set[str] = set()
        for wallet in wallets:
            _validate_wallet_record(wallet)
            wallet_id = wallet["wallet_id"]
            address = wallet["address"]
            if wallet_id in seen_ids:
                raise VaultDocumentError("Duplicate wallet_id in vault")
            if address in seen_addresses:
                raise VaultDocumentError("Duplicate wallet address in vault")
            seen_ids.add(wallet_id)
            seen_addresses.add(address)


def _validate_wallet_record(wallet: Any) -> None:
    if not isinstance(wallet, dict):
        raise VaultDocumentError("Wallet record must be a JSON object")
    expected = {
        "wallet_id", "label", "network", "address", "derivation_path", "created_at", "mnemonic"
    }
    if set(wallet) != expected:
        raise VaultDocumentError("Wallet record contains missing or unexpected fields")

    wallet_id = wallet["wallet_id"]
    if not isinstance(wallet_id, str) or not _WALLET_ID.fullmatch(wallet_id):
        raise VaultDocumentError("Wallet ID must be a canonical lowercase UUID")
    _validate_label(wallet["label"])

    network = wallet["network"]
    if not isinstance(network, str) or not _IDENTIFIER.fullmatch(network):
        raise VaultDocumentError("Wallet network is invalid")
    if network != "bitcoin-mainnet":
        raise VaultDocumentError(
            "This vault schema version supports Bitcoin Mainnet wallet records only"
        )

    address = wallet["address"]
    if (
        not isinstance(address, str)
        or len(address) != 42
        or not address.startswith("bc1q")
        or address != address.lower()
    ):
        raise VaultDocumentError("Wallet address is not a supported Bitcoin Mainnet P2WPKH address")
    if not address.isascii() or any(char.isspace() or ord(char) < 33 for char in address):
        raise VaultDocumentError("Wallet address contains invalid characters")

    if wallet["derivation_path"] != _RECEIVE_PATH:
        raise VaultDocumentError("Unsupported Bitcoin derivation path in wallet record")

    created_at = wallet["created_at"]
    if not isinstance(created_at, str):
        raise VaultDocumentError("Wallet created_at must be an ISO 8601 timestamp")
    try:
        timestamp = datetime.fromisoformat(created_at)
    except ValueError as exc:
        raise VaultDocumentError("Wallet created_at must be an ISO 8601 timestamp") from exc
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise VaultDocumentError("Wallet created_at must include a timezone")

    mnemonic = wallet["mnemonic"]
    if (
        not isinstance(mnemonic, str)
        or len(mnemonic) > 300
        or not _MNEMONIC.fullmatch(mnemonic)
    ):
        raise VaultDocumentError(
            "Wallet recovery phrase must be a normalized 12- or 24-word English phrase"
        )


def _validate_label(label: object) -> None:
    if not isinstance(label, str) or not label or label.strip() != label:
        raise VaultDocumentError("Label must be a non-empty string without surrounding spaces")
    if len(label) > MAX_LABEL_LENGTH:
        raise VaultDocumentError(f"Label must be {MAX_LABEL_LENGTH} characters or fewer")
    if any(ord(char) < 32 or ord(char) == 127 for char in label):
        raise VaultDocumentError("Label must not contain control characters")


def _validate_new_password(password: object) -> None:
    if not isinstance(password, str):
        raise VaultDocumentError("Vault password must be a string")
    if len(password) < MIN_VAULT_PASSWORD_LENGTH:
        raise VaultDocumentError(
            f"Vault password must contain at least {MIN_VAULT_PASSWORD_LENGTH} characters"
        )
