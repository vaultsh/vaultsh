"""Solana read-only RPC policy tests; no live network calls are made."""
from __future__ import annotations

import pytest

from vaultsh.networks.base import NetworkError
from vaultsh.networks.solana.client import MAINNET_GENESIS_HASH, SolanaRpcClient, sol_to_lamports, validate_solana_rpc_endpoint


def test_solana_endpoint_validation() -> None:
    assert validate_solana_rpc_endpoint("https://rpc.example/solana") == "https://rpc.example/solana"
    assert validate_solana_rpc_endpoint("http://127.0.0.1:8899") == "http://127.0.0.1:8899"
    with pytest.raises(NetworkError):
        validate_solana_rpc_endpoint("http://rpc.example")
    with pytest.raises(NetworkError):
        validate_solana_rpc_endpoint("https://user:pass@rpc.example")


def test_solana_balance_requires_mainnet_genesis(monkeypatch: pytest.MonkeyPatch) -> None:
    client = SolanaRpcClient("https://rpc.example", opener=object())
    calls = []
    def fake_call(method, params=None, request_id=1):
        calls.append(method)
        if method == "getGenesisHash":
            return MAINNET_GENESIS_HASH
        if method == "getBalance":
            return {"context": {"slot": 1}, "value": 2_000_000_000}
        raise AssertionError(method)
    monkeypatch.setattr(client, "call", fake_call)
    assert client.get_balance("11111111111111111111111111111111") == 2_000_000_000
    assert calls == ["getGenesisHash", "getBalance"]


def test_solana_rejects_wrong_genesis_hash(monkeypatch: pytest.MonkeyPatch) -> None:
    client = SolanaRpcClient("https://rpc.example", opener=object())
    monkeypatch.setattr(client, "call", lambda method, params=None, request_id=1: "wrong-genesis")
    with pytest.raises(NetworkError, match="Mainnet"):
        client.ensure_mainnet()


def test_sol_precision_is_exact() -> None:
    assert sol_to_lamports("2.000000001") == 2_000_000_001
