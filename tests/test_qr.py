"""Public-address QR tests; secret phrases are rejected by the QR helper."""
from __future__ import annotations

from pathlib import Path

import pytest

from vaultsh.ui.qr import QrError, render_address_qr, save_address_qr

ADDRESS = "0x" + "12" * 20


def test_render_address_qr_is_ascii_and_nonempty() -> None:
    result = render_address_qr(ADDRESS)
    assert result
    assert "\n" in result
    assert "██" in result


def test_save_address_qr_creates_png(tmp_path: Path) -> None:
    path = save_address_qr(ADDRESS, tmp_path / "address.png")
    assert path.exists()
    assert path.suffix == ".png"
    assert path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_save_address_qr_refuses_overwrite(tmp_path: Path) -> None:
    path = tmp_path / "address.png"
    path.write_bytes(b"keep")
    with pytest.raises(FileExistsError):
        save_address_qr(ADDRESS, path)
    assert path.read_bytes() == b"keep"


def test_qr_rejects_recovery_phrase_whitespace() -> None:
    with pytest.raises(QrError, match="recovery phrases"):
        render_address_qr("abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about")


def test_qr_rejects_unprefixed_private_key_like_hex() -> None:
    with pytest.raises(QrError, match="public BTC, EVM, Monero, or Solana"):
        render_address_qr("ab" * 32)


def test_qr_rejects_random_single_token_text() -> None:
    with pytest.raises(QrError, match="public BTC, EVM, Monero, or Solana"):
        render_address_qr("this-is-not-a-wallet-address")


def test_qr_accepts_recognized_bitcoin_mainnet_legacy_shape() -> None:
    # Format recognition is intentionally not a full checksum verifier; the QR
    # encodes the exact public address string and does not touch secret material.
    assert render_address_qr("1BoatSLRHtKNngkdXEeobR76b53LETtpyT")
