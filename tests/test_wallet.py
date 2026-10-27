import pytest

from vaultsh.core.wallet import WalletSummary


def test_wallet_summary_accepts_safe_metadata() -> None:
    wallet = WalletSummary(wallet_id="wallet-1", network="bitcoin-mainnet", label="Savings")
    assert wallet.wallet_id == "wallet-1"
    assert wallet.network == "bitcoin-mainnet"
    assert wallet.label == "Savings"


def test_wallet_summary_rejects_unsafe_identifiers() -> None:
    with pytest.raises(ValueError):
        WalletSummary(wallet_id="../secret", network="bitcoin")
    with pytest.raises(ValueError):
        WalletSummary(wallet_id="wallet-1", network="bitcoin\nmainnet")


def test_wallet_summary_rejects_control_characters_in_label() -> None:
    with pytest.raises(ValueError, match="control characters"):
        WalletSummary(wallet_id="wallet-1", network="bitcoin", label="name\nother")
