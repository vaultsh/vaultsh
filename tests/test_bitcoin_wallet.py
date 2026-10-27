"""Bitcoin tests include the published BIP-84 first-address test vector."""

from importlib.util import find_spec

import pytest

from vaultsh.networks.bitcoin.wallet import (
    BitcoinWalletError,
    derive_first_receive_address,
    generate_mnemonic,
)

MNEMONIC_VECTOR = (
    "abandon abandon abandon abandon abandon abandon "
    "abandon abandon abandon abandon abandon about"
)
BIP84_FIRST_ADDRESS = "bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu"


def test_official_bip84_first_receive_address_vector() -> None:
    if find_spec("embit") is None:
        pytest.skip("embit is a project dependency but is not installed in this test environment")
    wallet = derive_first_receive_address(MNEMONIC_VECTOR)
    assert wallet.address == BIP84_FIRST_ADDRESS
    assert wallet.derivation_path == "m/84'/0'/0'/0/0"
    assert wallet.network == "bitcoin-mainnet"
    assert wallet.mnemonic == MNEMONIC_VECTOR
    assert "mnemonic=" not in repr(wallet)


def test_generated_phrase_is_a_valid_twelve_word_phrase() -> None:
    if find_spec("embit") is None:
        pytest.skip("embit is a project dependency but is not installed in this test environment")
    phrase = generate_mnemonic()
    assert len(phrase.split()) == 12
    assert derive_first_receive_address(phrase).address.startswith("bc1q")


def test_missing_dependency_has_actionable_error_when_not_installed() -> None:
    if find_spec("embit") is not None:
        pytest.skip("embit is available in this environment")
    with pytest.raises(BitcoinWalletError, match="requires embit"):
        generate_mnemonic()


def test_invalid_phrase_is_not_reported_with_input_echo() -> None:
    if find_spec("embit") is None:
        pytest.skip("phrase validation is delegated to the embit BIP-39 implementation")
    bad_phrase = (
        "abandon abandon abandon abandon abandon abandon "
        "abandon abandon abandon abandon abandon abandon"
    )
    with pytest.raises(BitcoinWalletError, match="Invalid BIP-39") as exc_info:
        derive_first_receive_address(bad_phrase)
    assert bad_phrase not in str(exc_info.value)


def test_bitcoin_payment_signs_a_local_p2wpkh_transaction_without_broadcasting() -> None:
    pytest.importorskip("embit")
    from vaultsh.networks.bitcoin.transfer import prepare_bitcoin_transfer
    from vaultsh.networks.bitcoin.wallet import derive_first_receive_address

    mnemonic_a = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
    mnemonic_b = "test test test test test test test test test test test junk"
    sender = derive_first_receive_address(mnemonic_a).address
    destination = derive_first_receive_address(mnemonic_b).address
    preview = prepare_bitcoin_transfer(
        mnemonic=mnemonic_a,
        expected_sender=sender,
        destination=destination,
        amount="0.001",
        utxos=[{"txid": "11" * 32, "vout": 0, "value": 1_000_000}],
        fee_rate_sat_vb=1,
        max_fee_sats=1_000,
    )
    assert preview.sender == sender
    assert preview.destination == destination
    assert preview.amount_sats == 100_000
    assert preview.raw_transaction_hex
    assert len(preview.raw_transaction_hex) % 2 == 0
    assert preview.fee_sats <= 1_000
