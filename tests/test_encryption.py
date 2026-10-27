import pytest

from vaultsh.crypto.encryption import EncryptionError, decrypt_bytes, encrypt_bytes


def test_encrypt_decrypt_round_trip() -> None:
    message = b"vaultsh test fixture - not a real seed"
    encrypted = encrypt_bytes(message, "a-strong-test-passphrase")
    assert encrypted != message
    assert decrypt_bytes(encrypted, "a-strong-test-passphrase") == message


def test_wrong_password_fails_authentication() -> None:
    encrypted = encrypt_bytes(b"secret test data", "right-password")
    with pytest.raises(EncryptionError, match="Invalid encrypted data or password"):
        decrypt_bytes(encrypted, "wrong-password")


def test_modified_ciphertext_fails_authentication() -> None:
    encrypted = bytearray(encrypt_bytes(b"payload", "password"))
    encrypted[-1] ^= 0x01
    with pytest.raises(EncryptionError):
        decrypt_bytes(bytes(encrypted), "password")


def test_malformed_envelope_is_rejected() -> None:
    with pytest.raises(EncryptionError):
        decrypt_bytes(b"not a vault", "password")


def test_encrypt_rejects_empty_password() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        encrypt_bytes(b"data", "")
