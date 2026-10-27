"""Offline tests for bounded Esplora address transaction history."""

from __future__ import annotations

import json
from typing import Any

import pytest

import vaultsh.networks.bitcoin.client as bitcoin_client
from vaultsh.networks.base import NetworkError
from vaultsh.networks.bitcoin.client import BitcoinAddressTransaction, BitcoinEsploraClient

ADDRESS = "bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu"
TXID = "a" * 64


class FakeResponse:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def read(self, size: int = -1) -> bytes:
        return self.payload if size < 0 else self.payload[:size]


class FakeOpener:
    def __init__(self, payload: Any) -> None:
        self.payload = payload
        self.request: Any = None

    def open(self, request: Any, timeout: float) -> FakeResponse:
        self.request = request
        raw = self.payload if isinstance(self.payload, bytes) else json.dumps(self.payload).encode()
        return FakeResponse(raw)


def test_transaction_history_parses_confirmed_and_unconfirmed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bitcoin_client, "_validate_mainnet_address", lambda _address: None)
    payload = [
        {
            "txid": TXID,
            "status": {"confirmed": True, "block_height": 900, "block_time": 1_700_000_000},
            "fee": 1200,
        },
        {"txid": "b" * 64, "status": {"confirmed": False}, "fee": 0},
    ]
    opener = FakeOpener(payload)
    client = BitcoinEsploraClient("https://explorer.example/api", opener=opener)
    result = client.get_address_transactions(ADDRESS, limit=2)
    assert result == (
        BitcoinAddressTransaction(TXID, True, 900, 1_700_000_000, 1200),
        BitcoinAddressTransaction("b" * 64, False, None, None, 0),
    )
    assert opener.request.full_url == f"https://explorer.example/api/address/{ADDRESS}/txs"


def test_transaction_history_limits_results(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bitcoin_client, "_validate_mainnet_address", lambda _address: None)
    payload = [
        {"txid": f"{index:064x}", "status": {"confirmed": False}, "fee": 1}
        for index in range(5)
    ]
    result = BitcoinEsploraClient(
        "https://explorer.example/api", opener=FakeOpener(payload)
    ).get_address_transactions(ADDRESS, limit=2)
    assert len(result) == 2


def test_transaction_history_rejects_malformed_ids(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bitcoin_client, "_validate_mainnet_address", lambda _address: None)
    payload = [{"txid": "not-a-txid", "status": {"confirmed": False}}]
    client = BitcoinEsploraClient("https://explorer.example/api", opener=FakeOpener(payload))
    with pytest.raises(NetworkError, match="transaction ID"):
        client.get_address_transactions(ADDRESS)


def test_transaction_history_rejects_missing_confirmed_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(bitcoin_client, "_validate_mainnet_address", lambda _address: None)
    payload = [{"txid": TXID, "status": {"confirmed": True}}]
    client = BitcoinEsploraClient("https://explorer.example/api", opener=FakeOpener(payload))
    with pytest.raises(NetworkError, match="block metadata"):
        client.get_address_transactions(ADDRESS)


def test_transaction_history_limit_must_be_bounded() -> None:
    client = BitcoinEsploraClient("https://explorer.example/api", opener=FakeOpener([]))
    with pytest.raises(NetworkError, match="from 1 to 25"):
        client.get_address_transactions(ADDRESS, limit=26)
