"""Unit tests for the read-only Ethereum JSON-RPC adapter; no live network is used."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError

import pytest

from vaultsh.networks.base import NetworkError
from vaultsh.networks.ethereum.client import (
    EthereumAddressBalance,
    EvmJsonRpcClient,
    format_eth,
    get_evm_network_profile,
    validate_ethereum_address,
    validate_rpc_endpoint,
)

ADDRESS = "0xde709f2102306220921060314715629080e2fb77"


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
    def __init__(self, *payloads: Any) -> None:
        self.payloads = list(payloads)
        self.requests: list[Any] = []
        self.timeouts: list[float] = []

    def open(self, request: Any, timeout: float) -> FakeResponse:
        self.requests.append(request)
        self.timeouts.append(timeout)
        payload = self.payloads.pop(0)
        if isinstance(payload, bytes):
            raw = payload
        else:
            raw = json.dumps(payload).encode("utf-8")
        return FakeResponse(raw)


def rpc_result(request_id: int, result: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def test_evm_balance_uses_mainnet_and_exact_wei() -> None:
    opener = FakeOpener(rpc_result(1, "0x1"), rpc_result(2, "0x16345785d8a0000"))
    client = EvmJsonRpcClient("https://rpc.example", timeout_seconds=8, opener=opener)

    result = client.get_address_balance(ADDRESS)

    assert result == EthereumAddressBalance(address=ADDRESS, balance_wei=100_000_000_000_000_000)
    assert result.chain_id == 1
    assert len(opener.requests) == 2
    first = json.loads(opener.requests[0].data)
    second = json.loads(opener.requests[1].data)
    assert first == {"jsonrpc": "2.0", "method": "eth_chainId", "params": [], "id": 1}
    assert second == {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [ADDRESS, "latest"],
        "id": 2,
    }
    assert all(request.get_method() == "POST" for request in opener.requests)
    assert opener.timeouts == [8.0, 8.0]


def test_refuses_wrong_chain_before_querying_balance() -> None:
    opener = FakeOpener(rpc_result(1, "0x89"))  # Polygon Mainnet
    client = EvmJsonRpcClient("https://rpc.example", opener=opener)
    with pytest.raises(NetworkError, match="not Ethereum Mainnet"):
        client.get_address_balance(ADDRESS)
    assert len(opener.requests) == 1


def test_invalid_rpc_response_id_is_rejected() -> None:
    opener = FakeOpener(rpc_result(77, "0x1"))
    client = EvmJsonRpcClient("https://rpc.example", opener=opener)
    with pytest.raises(NetworkError, match="did not match"):
        client.get_address_balance(ADDRESS)


def test_rpc_error_is_sanitized() -> None:
    opener = FakeOpener({"jsonrpc": "2.0", "id": 1, "error": {"message": "sensitive detail"}})
    client = EvmJsonRpcClient("https://rpc.example", opener=opener)
    with pytest.raises(NetworkError, match="reported an error") as exc:
        client.get_address_balance(ADDRESS)
    assert "sensitive detail" not in str(exc.value)


def test_invalid_balance_quantity_is_rejected() -> None:
    opener = FakeOpener(rpc_result(1, "0x1"), rpc_result(2, "01"))
    client = EvmJsonRpcClient("https://rpc.example", opener=opener)
    with pytest.raises(NetworkError, match="invalid balance quantity"):
        client.get_address_balance(ADDRESS)


def test_invalid_address_is_rejected_before_network_call() -> None:
    opener = FakeOpener(rpc_result(1, "0x1"))
    client = EvmJsonRpcClient("https://rpc.example", opener=opener)
    with pytest.raises(NetworkError, match="40 hexadecimal"):
        client.get_address_balance("0x1234")
    assert opener.requests == []


def test_mixed_case_checksum_is_verified_when_dependency_is_installed() -> None:
    pytest.importorskip("eth_utils")
    valid = "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed"
    invalid = "0x5aAeb6053f3E94C9b9A09f33669435E7Ef1BeAed"
    assert validate_ethereum_address(valid) == valid
    with pytest.raises(NetworkError, match="checksum"):
        validate_ethereum_address(invalid)


@pytest.mark.parametrize(
    "endpoint",
    [
        "http://rpc.example",
        "https://user:pass@rpc.example",
        "https://rpc.example/?key=secret",
        "https://rpc.example/#fragment",
        "https://rpc.example/../node",
        "file:///etc/passwd",
    ],
)
def test_unsafe_rpc_endpoints_are_rejected(endpoint: str) -> None:
    with pytest.raises(NetworkError):
        validate_rpc_endpoint(endpoint)


def test_loopback_http_endpoint_is_allowed() -> None:
    assert validate_rpc_endpoint("http://127.0.0.1:8545/") == "http://127.0.0.1:8545"


def test_http_redirect_is_not_followed() -> None:
    class RedirectOpener:
        def open(self, request: Any, timeout: float) -> Any:
            raise HTTPError(request.full_url, 302, "Found", {}, None)

    client = EvmJsonRpcClient("https://rpc.example", opener=RedirectOpener())
    with pytest.raises(NetworkError, match="redirects are disabled"):
        client.get_address_balance(ADDRESS)


def test_response_size_limit_is_enforced() -> None:
    opener = FakeOpener(b"{" + b" " * 80)
    client = EvmJsonRpcClient("https://rpc.example", opener=opener, max_response_bytes=10)
    with pytest.raises(NetworkError, match="size limit"):
        client.get_address_balance(ADDRESS)


def test_eth_format_is_exact() -> None:
    assert format_eth(0) == "0"
    assert format_eth(10**18) == "1"
    assert format_eth(1_234_567_890_000_000_000) == "1.23456789"
    assert format_eth(1) == "0.000000000000000001"


@pytest.mark.parametrize(
    ("network", "chain_id", "symbol"),
    [
        ("ethereum", 1, "ETH"),
        ("polygon", 137, "POL"),
        ("arbitrum", 42161, "ETH"),
        ("optimism", 10, "ETH"),
        ("base", 8453, "ETH"),
    ],
)
def test_supported_evm_profiles_enforce_expected_chain(
    network: str, chain_id: int, symbol: str
) -> None:
    profile = get_evm_network_profile(network)
    assert profile.chain_id == chain_id
    assert profile.asset_symbol == symbol
    opener = FakeOpener(rpc_result(1, hex(chain_id)), rpc_result(2, "0x0"))
    client = EvmJsonRpcClient(
        "https://rpc.example",
        opener=opener,
        expected_chain_id=profile.chain_id,
        network_name=profile.name,
        asset_symbol=profile.asset_symbol,
    )
    result = client.get_address_balance(ADDRESS)
    assert result.chain_id == chain_id
    assert result.balance_base_units == result.balance_wei == 0
    assert result.asset_symbol == symbol
    assert result.network_name == profile.name


def test_unknown_evm_network_is_rejected_without_guessing() -> None:
    with pytest.raises(NetworkError, match="Unsupported EVM network"):
        get_evm_network_profile("fantasy-chain")


def test_evm_transfer_is_signed_locally_and_not_broadcast_by_prepare(monkeypatch) -> None:
    pytest.importorskip("eth_account")
    from eth_account import Account
    from vaultsh.networks.ethereum.transfer import prepare_evm_transfer

    private_key = bytes.fromhex("ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80")
    expected_sender = Account.from_key(private_key).address
    monkeypatch.setattr("vaultsh.networks.ethereum.transfer.derive_evm_private_key", lambda _mnemonic: private_key)

    class FakeRpc:
        def __init__(self):
            self.calls = []
        def _rpc_call(self, method, params, request_id):
            self.calls.append(method)
            return {
                "eth_chainId": "0x1",
                "eth_getTransactionCount": "0x0",
                "eth_gasPrice": "0x3b9aca00",
                "eth_getBalance": "0x4563918244f40000",
                "eth_estimateGas": "0x5208",
            }[method]

    fake = FakeRpc()
    preview = prepare_evm_transfer(
        endpoint="https://rpc.example",
        network="ethereum",
        mnemonic="test test test test test test test test test test test junk",
        expected_sender=expected_sender,
        destination="0x000000000000000000000000000000000000dead",
        amount="0.01",
        max_fee_native="0.001",
        client=fake,
    )
    assert preview.sender.lower() == expected_sender.lower()
    assert preview.amount_base_units == 10**16
    assert preview.chain_id == 1
    assert preview.raw_signed_transaction.startswith("0x")
    assert "eth_sendRawTransaction" not in fake.calls
