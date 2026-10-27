"""Pure amount parsing tests; never contact a blockchain node."""

from __future__ import annotations

import pytest

from vaultsh.networks.base import NetworkError
from vaultsh.networks.bitcoin.transfer import btc_to_sats
from vaultsh.networks.ethereum.transfer import parse_decimal_units
from vaultsh.networks.monero.rpc import format_xmr, xmr_to_atomic
from vaultsh.networks.solana.client import sol_to_lamports


@pytest.mark.parametrize(
    ("text", "expected"),
    [("0.00000001", 1), ("1", 100_000_000), ("1.25000000", 125_000_000)],
)
def test_btc_amount_conversion(text: str, expected: int) -> None:
    assert btc_to_sats(text) == expected


@pytest.mark.parametrize("text", ["0", "-1", "nan", "inf", "0.000000001", "1e-8", ""])
def test_btc_amount_rejects_invalid_precision_or_value(text: str) -> None:
    with pytest.raises(NetworkError):
        btc_to_sats(text)


def test_evm_amount_conversion_uses_exact_base_units() -> None:
    assert parse_decimal_units("1.000000000000000001", decimals=18, asset_symbol="ETH") == 1_000_000_000_000_000_001


@pytest.mark.parametrize("text", ["0", "-1", "1.0000000000000000001", "nan", "Infinity"])
def test_evm_amount_rejects_invalid_values(text: str) -> None:
    with pytest.raises(NetworkError):
        parse_decimal_units(text, decimals=18, asset_symbol="ETH")


def test_sol_amount_conversion() -> None:
    assert sol_to_lamports("1.000000001") == 1_000_000_001


@pytest.mark.parametrize("text", ["0", "-0.1", "0.0000000001", "NaN"])
def test_sol_amount_rejects_invalid_values(text: str) -> None:
    with pytest.raises(NetworkError):
        sol_to_lamports(text)


def test_xmr_amount_conversion_and_formatting() -> None:
    assert xmr_to_atomic("1.000000000001") == 1_000_000_000_001
    assert format_xmr(1_000_000_000_001) == "1.000000000001"
    assert format_xmr(1_000_000_000_000) == "1"


@pytest.mark.parametrize("text", ["0", "-1", "1e-12", "0.0000000000001", "NaN", "inf"])
def test_xmr_amount_rejects_invalid_values(text: str) -> None:
    with pytest.raises(NetworkError):
        xmr_to_atomic(text)
