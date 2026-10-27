"""Monero RPC adapter tests use a fake call method and never contact a node."""

from __future__ import annotations

from typing import Any

import pytest

from vaultsh.networks.base import NetworkError
from vaultsh.networks.monero.rpc import MoneroWalletRpcClient, MoneroTransferPreview


HASH = "a" * 64
DESTINATION = "4" * 95


def make_client() -> MoneroWalletRpcClient:
    # An opener sentinel ensures tests cannot accidentally reach a real endpoint.
    return MoneroWalletRpcClient("http://127.0.0.1:18088/json_rpc", opener=object())


def test_monero_endpoint_is_loopback_only() -> None:
    assert MoneroWalletRpcClient._validate_local_endpoint("http://127.0.0.1:18088/json_rpc") == "http://127.0.0.1:18088/json_rpc"
    with pytest.raises(NetworkError):
        MoneroWalletRpcClient._validate_local_endpoint("http://monero-rpc.example/json_rpc")
    with pytest.raises(NetworkError):
        MoneroWalletRpcClient._validate_local_endpoint("https://127.0.0.1:18088/json_rpc")


def test_wallet_filename_rejects_path_traversal() -> None:
    with pytest.raises(NetworkError):
        MoneroWalletRpcClient._validate_wallet_name("../secrets")
    with pytest.raises(NetworkError):
        MoneroWalletRpcClient._validate_wallet_name("folder/wallet")
    assert MoneroWalletRpcClient._validate_wallet_name("main_wallet-1") == "main_wallet-1"


def test_prepare_transfer_uses_metadata_for_later_relay(monkeypatch: pytest.MonkeyPatch) -> None:
    client = make_client()
    calls: list[tuple[str, dict[str, Any], str]] = []

    def fake_call(method: str, params: dict[str, Any] | None = None, *, request_id: str = "vaultsh") -> dict[str, Any]:
        current = params or {}
        calls.append((method, current, request_id))
        if method == "validate_address":
            return {"valid": True, "nettype": "mainnet"}
        if method == "transfer":
            return {
                "amount": 1_000_000_000_000,
                "fee": 3_000_000,
                "tx_hash": HASH,
                "tx_metadata": "encoded-monero-metadata",
            }
        if method == "relay_tx":
            assert current["hex"] == "encoded-monero-metadata"
            return {"tx_hash": HASH}
        raise AssertionError(f"Unexpected method: {method}")

    monkeypatch.setattr(client, "call", fake_call)
    preview = client.prepare_transfer(destination=DESTINATION, amount="1")
    assert preview.destination == DESTINATION
    assert preview.amount_atomic == 1_000_000_000_000
    assert preview.fee_atomic == 3_000_000
    assert preview.tx_hash == HASH
    assert preview.tx_metadata == "encoded-monero-metadata"
    assert calls[1][1]["do_not_relay"] is True
    assert calls[1][1]["get_tx_metadata"] is True
    assert "get_tx_hex" not in calls[1][1]
    assert len(calls) == 2  # prepare never broadcasts
    assert client.relay_transfer(preview) == HASH
    assert calls[-1][0] == "relay_tx"


def test_prepare_transfer_rejects_non_mainnet_destination(monkeypatch: pytest.MonkeyPatch) -> None:
    client = make_client()
    monkeypatch.setattr(client, "call", lambda method, params=None, **kwargs: {"valid": True, "nettype": "stagenet"})
    with pytest.raises(NetworkError, match="Mainnet"):
        client.prepare_transfer(destination=DESTINATION, amount="1")


def test_monero_preview_hides_transaction_metadata_from_repr() -> None:
    preview = MoneroTransferPreview(DESTINATION, 1, 1, HASH, "secret-metadata")
    assert "secret-metadata" not in repr(preview)


def test_monero_own_address_must_be_mainnet(monkeypatch: pytest.MonkeyPatch) -> None:
    client = make_client()
    responses = {
        "get_address": {"addresses": [{"address": DESTINATION}]},
        "validate_address": {"valid": True, "nettype": "stagenet"},
    }
    monkeypatch.setattr(client, "call", lambda method, params=None, **kwargs: responses[method])
    with pytest.raises(NetworkError, match="Mainnet"):
        client.get_address()


def test_monero_own_mainnet_address_is_accepted(monkeypatch: pytest.MonkeyPatch) -> None:
    client = make_client()
    responses = {
        "get_address": {"addresses": [{"address": DESTINATION}]},
        "validate_address": {"valid": True, "nettype": "mainnet"},
    }
    monkeypatch.setattr(client, "call", lambda method, params=None, **kwargs: responses[method])
    assert client.get_address() == DESTINATION
