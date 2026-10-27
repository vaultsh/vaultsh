"""Authenticated encryption for local byte payloads.

This is a small envelope primitive, not a complete wallet-security design.
Passwords are processed with Scrypt and data is encrypted with AES-256-GCM.
The envelope is versioned and its KDF parameters are bounded before use.
"""

from __future__ import annotations

import os
import struct

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

MAGIC = b"VSHV"
FORMAT_VERSION = 1
SALT_LENGTH = 16
NONCE_LENGTH = 12
KEY_LENGTH = 32
DEFAULT_SCRYPT_N = 2**15
DEFAULT_SCRYPT_R = 8
DEFAULT_SCRYPT_P = 1
_MIN_SCRYPT_N = 2**14
_MAX_SCRYPT_N = 2**16
_MAX_SCRYPT_R = 8
_MAX_SCRYPT_P = 4
_HEADER = struct.Struct(">BIII")


class EncryptionError(ValueError):
    """Raised for malformed ciphertext or failed authenticated decryption."""


def _password_bytes(password: str) -> bytes:
    if not isinstance(password, str):
        raise TypeError("password must be a string")
    if not password:
        raise ValueError("password must not be empty")
    try:
        encoded = password.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError("password cannot be encoded as UTF-8") from exc
    if len(encoded) > 1024:
        raise ValueError("password must be 1024 UTF-8 bytes or fewer")
    return encoded


def _derive_key(password: bytes, salt: bytes, n: int, r: int, p: int) -> bytes:
    return Scrypt(salt=salt, length=KEY_LENGTH, n=n, r=r, p=p).derive(password)


def encrypt_bytes(
    plaintext: bytes,
    password: str,
    *,
    n: int = DEFAULT_SCRYPT_N,
    r: int = DEFAULT_SCRYPT_R,
    p: int = DEFAULT_SCRYPT_P,
) -> bytes:
    """Encrypt bytes into a self-describing authenticated envelope.

    Each invocation generates a fresh salt and nonce. Do not reuse this as a
    substitute for a reviewed wallet-vault format without independent review.
    """
    if not isinstance(plaintext, bytes):
        raise TypeError("plaintext must be bytes")
    _password = _password_bytes(password)
    _validate_scrypt_params(n, r, p)
    salt = os.urandom(SALT_LENGTH)
    nonce = os.urandom(NONCE_LENGTH)
    header = MAGIC + _HEADER.pack(FORMAT_VERSION, n, r, p) + salt + nonce
    key = _derive_key(_password, salt, n, r, p)
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, header)
    return header + ciphertext


def decrypt_bytes(envelope: bytes, password: str) -> bytes:
    """Authenticate and decrypt a payload produced by :func:`encrypt_bytes`.

    A wrong password and modified ciphertext raise the same public error to
    avoid exposing whether authentication failed due to password or tampering.
    """
    _password = _password_bytes(password)
    if not isinstance(envelope, bytes):
        raise TypeError("envelope must be bytes")
    minimum = len(MAGIC) + _HEADER.size + SALT_LENGTH + NONCE_LENGTH + 16
    if len(envelope) < minimum:
        raise EncryptionError("Invalid encrypted data or password")
    if not envelope.startswith(MAGIC):
        raise EncryptionError("Unsupported encrypted data format")

    offset = len(MAGIC)
    try:
        version, n, r, p = _HEADER.unpack(envelope[offset : offset + _HEADER.size])
    except struct.error as exc:
        raise EncryptionError("Invalid encrypted data or password") from exc
    if version != FORMAT_VERSION:
        raise EncryptionError(f"Unsupported encrypted-data version: {version}")
    try:
        _validate_scrypt_params(n, r, p)
    except ValueError as exc:
        raise EncryptionError("Unsafe or invalid KDF parameters in encrypted data") from exc

    offset += _HEADER.size
    salt = envelope[offset : offset + SALT_LENGTH]
    offset += SALT_LENGTH
    nonce = envelope[offset : offset + NONCE_LENGTH]
    offset += NONCE_LENGTH
    associated_data = envelope[:offset]
    ciphertext = envelope[offset:]

    try:
        key = _derive_key(_password, salt, n, r, p)
        return AESGCM(key).decrypt(nonce, ciphertext, associated_data)
    except (InvalidTag, ValueError) as exc:
        raise EncryptionError("Invalid encrypted data or password") from exc


def _validate_scrypt_params(n: int, r: int, p: int) -> None:
    if isinstance(n, bool) or not isinstance(n, int) or not (_MIN_SCRYPT_N <= n <= _MAX_SCRYPT_N):
        raise ValueError("Scrypt N must be between 2**14 and 2**16")
    if n & (n - 1):
        raise ValueError("Scrypt N must be a power of two")
    if isinstance(r, bool) or not isinstance(r, int) or not (1 <= r <= _MAX_SCRYPT_R):
        raise ValueError("Scrypt r must be between 1 and 8")
    if isinstance(p, bool) or not isinstance(p, int) or not (1 <= p <= _MAX_SCRYPT_P):
        raise ValueError("Scrypt p must be between 1 and 4")
