"""CLI tests for opt-in native EVM balance lookups; no live network is used."""

from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from vaultsh.cli import app
from vaultsh.networks.ethereum.client import EVM_NETWORKS, EthereumAddressBalance

runner = CliRunner()
ADDRESS = "0xde709f2102306220921060314715629080e2fb77"


def write_config(path: Path, *, networking: bool, tor: bool = False) -> None:
    path.write_text(
        "[app]\n"
        f"network_requests_enabled = {'true' if networking else 'false'}\n"
        f"tor_enabled = {'true' if tor else 'false'}\n"
        "request_timeout_seconds = 2.0\n",
        encoding="utf-8",
    )


class FakeEvmClient:
    calls: list[tuple[Any, ...]] = []

    def __init__(
        self,
        endpoint: str,
        *,
        timeout_seconds: float,
        expected_chain_id: int,
        network_name: str,
        asset_symbol: str,
    ) -> None:
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds
        self.expected_chain_id = expected_chain_id
        self.network_name = network_name
        self.asset_symbol = asset_symbol
        self.__class__.calls.append(
            ("init", endpoint, timeout_seconds, expected_chain_id, network_name, asset_symbol)
        )

    def get_address_balance(self, address: str) -> EthereumAddressBalance:
        self.__class__.calls.append(("balance", address))
        return EthereumAddressBalance(
            address=address,
            balance_wei=1_234_567_890_000_000_000,
            chain_id=self.expected_chain_id,
            network_name=self.network_name,
            asset_symbol=self.asset_symbol,
        )


def invoke_balance(config: Path, *, allow_network: bool = True) -> Any:
    args = [
        "ethereum", "balance", ADDRESS,
        "--endpoint", "https://rpc.example/path",
        "--config", str(config),
    ]
    if allow_network:
        args.append("--allow-network")
    return runner.invoke(app, args)


def test_ethereum_balance_requires_explicit_cli_opt_in(tmp_path: Path, monkeypatch: Any) -> None:
    config = tmp_path / "vaultsh.toml"
    write_config(config, networking=True)
    monkeypatch.setattr(
        "vaultsh.cli.EvmJsonRpcClient",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("must not connect")),
    )
    result = invoke_balance(config, allow_network=False)
    assert result.exit_code == 1
    assert "Network access is disabled" in result.stdout


def test_ethereum_balance_requires_config_opt_in(tmp_path: Path, monkeypatch: Any) -> None:
    config = tmp_path / "vaultsh.toml"
    write_config(config, networking=False)
    monkeypatch.setattr(
        "vaultsh.cli.EvmJsonRpcClient",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("must not connect")),
    )
    result = invoke_balance(config)
    assert result.exit_code == 1
    assert "Network access is disabled" in result.stdout


def test_ethereum_balance_refuses_direct_connection_when_tor_enabled(
    tmp_path: Path, monkeypatch: Any
) -> None:
    config = tmp_path / "vaultsh.toml"
    write_config(config, networking=True, tor=True)
    monkeypatch.setattr(
        "vaultsh.cli.EvmJsonRpcClient",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("must not connect")),
    )
    result = invoke_balance(config)
    assert result.exit_code == 1
    output = " ".join(result.stdout.lower().split())
    assert "not implemented" in output and "tor" in output


def test_ethereum_balance_uses_explicit_endpoint_and_formats_exact_value(
    tmp_path: Path, monkeypatch: Any
) -> None:
    config = tmp_path / "vaultsh.toml"
    write_config(config, networking=True)
    FakeEvmClient.calls.clear()
    monkeypatch.setattr("vaultsh.cli.EvmJsonRpcClient", FakeEvmClient)
    result = invoke_balance(config)
    assert result.exit_code == 0, result.stdout
    assert "Privacy notice" in result.stdout
    assert "1.23456789" in result.stdout
    assert str(1_234_567_890_000_000_000) in result.stdout
    assert "rpc.example" in result.stdout
    assert FakeEvmClient.calls == [
        ("init", "https://rpc.example/path", 2.0, 1, "Ethereum Mainnet", "ETH"),
        ("balance", ADDRESS),
    ]


def test_polygon_native_balance_uses_polygon_chain_profile(
    tmp_path: Path, monkeypatch: Any
) -> None:
    config = tmp_path / "vaultsh.toml"
    write_config(config, networking=True)
    FakeEvmClient.calls.clear()
    monkeypatch.setattr("vaultsh.cli.EvmJsonRpcClient", FakeEvmClient)
    result = runner.invoke(
        app,
        [
            "evm", "balance", ADDRESS,
            "--chain", "polygon",
            "--endpoint", "https://polygon-rpc.example",
            "--config", str(config),
            "--allow-network",
        ],
    )
    assert result.exit_code == 0, result.stdout
    assert "Polygon PoS Mainnet" in result.stdout
    assert "POL" in result.stdout
    assert ("init", "https://polygon-rpc.example", 2.0, 137, "Polygon PoS Mainnet", "POL") in FakeEvmClient.calls


def test_each_profile_has_explicit_unique_chain_id_and_native_symbol() -> None:
    assert EVM_NETWORKS["ethereum"].chain_id == 1
    assert EVM_NETWORKS["polygon"].chain_id == 137
    assert EVM_NETWORKS["arbitrum"].chain_id == 42161
    assert EVM_NETWORKS["optimism"].chain_id == 10
    assert EVM_NETWORKS["base"].chain_id == 8453
    assert EVM_NETWORKS["polygon"].asset_symbol == "POL"
