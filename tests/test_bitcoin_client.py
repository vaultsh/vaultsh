"""Unit tests for the explicit, read-only Esplora client; no live network is used."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError

import pytest

import vaultsh.networks.bitcoin.client as bitcoin_client
from vaultsh.networks.base import NetworkError
from vaultsh.networks.bitcoin.client import (
    BitcoinAddressBalance,
    BitcoinEsploraClient,
    format_btc,
    validate_esplora_endpoint,
)

ADDRESS = "bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu"


def _response_payload(
    *,
    chain_funded: int = 115_000_000,
    chain_spent: int = 15_000_000,
    mempool_funded: int = 3_000_000,
    mempool_spent: int = 1_000_000,
    address: str = ADDRESS,
) -> dict[str, Any]:
    return {
        "address": address,
        "chain_stats": {"funded_txo_sum": chain_funded, "spent_txo_sum": chain_spent},
        "mempool_stats": {
            "funded_txo_sum": mempool_funded,
            "spent_txo_sum": mempool_spent,
        },
    }


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
    def __init__(self, payload: bytes) -> None:
        self.response = FakeResponse(payload)
        self.request: Any = None
        self.timeout: float | None = None

    def open(self, request: Any, timeout: float) -> FakeResponse:
        self.request = request
        self.timeout = timeout
        return self.response


def test_esplora_balance_calculations_are_exact(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bitcoin_client, "_validate_mainnet_address", lambda _address: None)
    opener = FakeOpener(json.dumps(_response_payload()).encode())
    client = BitcoinEsploraClient(
        "https://explorer.example/api/", timeout_seconds=7, opener=opener
    )

    result = client.get_address_balance(ADDRESS)

    assert result == BitcoinAddressBalance(
        address=ADDRESS,
        confirmed_sats=100_000_000,
        unconfirmed_sats=2_000_000,
    )
    assert result.estimated_total_sats == 102_000_000
    assert opener.timeout == 7.0
    assert opener.request.full_url == f"https://explorer.example/api/address/{ADDRESS}"
    assert opener.request.get_method() == "GET"
    assert opener.request.get_header("Accept") == "application/json"


def test_lifetime_output_counters_can_exceed_supply_when_net_balance_is_valid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(bitcoin_client, "_validate_mainnet_address", lambda _address: None)
    high_counter = 3 * bitcoin_client.MAX_MONEY_SATS
    payload = _response_payload(
        chain_funded=high_counter,
        chain_spent=high_counter - 50_000_000,
        mempool_funded=high_counter,
        mempool_spent=high_counter - 25_000_000,
    )
    client = BitcoinEsploraClient(
        "https://explorer.example/api", opener=FakeOpener(json.dumps(payload).encode())
    )
    result = client.get_address_balance(ADDRESS)
    assert result.confirmed_sats == 50_000_000
    assert result.unconfirmed_sats == 25_000_000


def test_negative_unconfirmed_net_change_is_preserved(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bitcoin_client, "_validate_mainnet_address", lambda _address: None)
    payload = _response_payload(mempool_funded=0, mempool_spent=3_000_000)
    result = BitcoinEsploraClient(
        "https://explorer.example/api", opener=FakeOpener(json.dumps(payload).encode())
    ).get_address_balance(ADDRESS)
    assert result.unconfirmed_sats == -3_000_000
    assert result.estimated_total_sats == 97_000_000


def test_endpoint_requires_https_for_remote_hosts() -> None:
    assert validate_esplora_endpoint("https://explorer.example/api/") == (
        "https://explorer.example/api"
    )
    with pytest.raises(NetworkError, match="Plain HTTP"):
        validate_esplora_endpoint("http://explorer.example/api")


@pytest.mark.parametrize(
    "endpoint",
    [
        "https://user:password@explorer.example/api",
        "https://explorer.example/api?token=secret",
        "https://explorer.example/api#fragment",
        "https://explorer.example/api/../internal",
        "file:///etc/passwd",
        "https://explorer.example:bad/api",
    ],
)
def test_endpoint_rejects_unsafe_or_malformed_urls(endpoint: str) -> None:
    with pytest.raises(NetworkError):
        validate_esplora_endpoint(endpoint)


def test_plain_http_is_allowed_only_on_loopback() -> None:
    assert validate_esplora_endpoint("http://127.0.0.1:3002/api") == (
        "http://127.0.0.1:3002/api"
    )
    assert validate_esplora_endpoint("http://localhost:3002/api") == (
        "http://localhost:3002/api"
    )
    with pytest.raises(NetworkError):
        validate_esplora_endpoint("http://192.168.1.10:3002/api")


def test_invalid_address_prefix_is_rejected_before_http(monkeypatch: pytest.MonkeyPatch) -> None:
    opener = FakeOpener(b"{}")
    client = BitcoinEsploraClient("https://explorer.example/api", opener=opener)
    with pytest.raises(NetworkError, match="Mainnet"):
        client.get_address_balance("tb1qtestnet-address")
    assert opener.request is None


def test_malformed_esplora_json_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bitcoin_client, "_validate_mainnet_address", lambda _address: None)
    client = BitcoinEsploraClient(
        "https://explorer.example/api", opener=FakeOpener(b"not-json")
    )
    with pytest.raises(NetworkError, match="invalid JSON"):
        client.get_address_balance(ADDRESS)


def test_response_address_must_match_request(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bitcoin_client, "_validate_mainnet_address", lambda _address: None)
    payload = _response_payload(address="bc1qwrongaddress")
    client = BitcoinEsploraClient(
        "https://explorer.example/api", opener=FakeOpener(json.dumps(payload).encode())
    )
    with pytest.raises(NetworkError, match="did not match"):
        client.get_address_balance(ADDRESS)


def test_invalid_stats_and_confirmed_negative_balance_are_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(bitcoin_client, "_validate_mainnet_address", lambda _address: None)
    bad_type = _response_payload()
    bad_type["chain_stats"]["funded_txo_sum"] = True
    client = BitcoinEsploraClient(
        "https://explorer.example/api", opener=FakeOpener(json.dumps(bad_type).encode())
    )
    with pytest.raises(NetworkError, match="satoshi values"):
        client.get_address_balance(ADDRESS)

    impossible = _response_payload(chain_funded=10, chain_spent=20)
    client = BitcoinEsploraClient(
        "https://explorer.example/api", opener=FakeOpener(json.dumps(impossible).encode())
    )
    with pytest.raises(NetworkError, match="impossible confirmed"):
        client.get_address_balance(ADDRESS)


def test_http_redirect_is_reported_and_not_followed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bitcoin_client, "_validate_mainnet_address", lambda _address: None)

    class RedirectOpener:
        def open(self, request: Any, timeout: float) -> Any:
            raise HTTPError(request.full_url, 302, "Found", {}, None)

    client = BitcoinEsploraClient(
        "https://explorer.example/api", opener=RedirectOpener()
    )
    with pytest.raises(NetworkError, match="redirects are disabled"):
        client.get_address_balance(ADDRESS)


def test_impossible_estimated_balance_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bitcoin_client, "_validate_mainnet_address", lambda _address: None)
    payload = _response_payload(
        chain_funded=bitcoin_client.MAX_MONEY_SATS,
        chain_spent=0,
        mempool_funded=1,
        mempool_spent=0,
    )
    client = BitcoinEsploraClient(
        "https://explorer.example/api", opener=FakeOpener(json.dumps(payload).encode())
    )
    with pytest.raises(NetworkError, match="impossible estimated balance"):
        client.get_address_balance(ADDRESS)


def test_response_size_limit_is_enforced(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bitcoin_client, "_validate_mainnet_address", lambda _address: None)
    client = BitcoinEsploraClient(
        "https://explorer.example/api",
        opener=FakeOpener(b"{" + (b" " * 100)),
        max_response_bytes=10,
    )
    with pytest.raises(NetworkError, match="size limit"):
        client.get_address_balance(ADDRESS)


def test_btc_formatting_never_uses_floating_point() -> None:
    assert format_btc(0) == "0.00000000"
    assert format_btc(100_000_000) == "1.00000000"
    assert format_btc(12_345_678) == "0.12345678"
    assert format_btc(-1) == "-0.00000001"
