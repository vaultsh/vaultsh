"""CLI tests for network opt-in and the Bitcoin address balance command."""

from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from vaultsh.cli import app
from vaultsh.networks.bitcoin.client import BitcoinAddressBalance

runner = CliRunner()
ADDRESS = "bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu"


def _write_config(path: Path, *, networking: bool, tor: bool = False) -> None:
    path.write_text(
        "[app]\n"
        "telemetry_enabled = false\n"
        f"network_requests_enabled = {'true' if networking else 'false'}\n"
        f"tor_enabled = {'true' if tor else 'false'}\n"
        "request_timeout_seconds = 2.0\n",
        encoding="utf-8",
    )


class FakeBitcoinClient:
    calls: list[tuple[str, str, float]] = []

    def __init__(self, endpoint: str, *, timeout_seconds: float) -> None:
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds
        self.__class__.calls.append((endpoint, "init", timeout_seconds))

    def get_address_balance(self, address: str) -> BitcoinAddressBalance:
        self.__class__.calls.append((self.endpoint, address, self.timeout_seconds))
        return BitcoinAddressBalance(
            address=address,
            confirmed_sats=123_456_789,
            unconfirmed_sats=-12_345,
        )


def test_balance_command_requires_both_network_flag_and_config(
    tmp_path: Path, monkeypatch: Any
) -> None:
    config = tmp_path / "vaultsh.toml"
    _write_config(config, networking=True)

    def forbidden_client(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("network client must not be constructed without explicit CLI opt-in")

    monkeypatch.setattr("vaultsh.cli.BitcoinEsploraClient", forbidden_client)
    result = runner.invoke(
        app,
        [
            "bitcoin", "balance", ADDRESS,
            "--endpoint", "https://explorer.example/api",
            "--config", str(config),
        ],
    )
    assert result.exit_code == 1
    assert "Network access is disabled" in result.stdout


def test_balance_command_requires_config_permission_even_with_flag(
    tmp_path: Path, monkeypatch: Any
) -> None:
    config = tmp_path / "vaultsh.toml"
    _write_config(config, networking=False)

    def forbidden_client(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError(
            "network client must not be constructed while config disables networking"
        )

    monkeypatch.setattr("vaultsh.cli.BitcoinEsploraClient", forbidden_client)
    result = runner.invoke(
        app,
        [
            "bitcoin", "balance", ADDRESS,
            "--endpoint", "https://explorer.example/api",
            "--config", str(config), "--allow-network",
        ],
    )
    assert result.exit_code == 1
    assert "Network access is disabled" in result.stdout


def test_balance_command_refuses_direct_access_when_tor_is_enabled(
    tmp_path: Path, monkeypatch: Any
) -> None:
    config = tmp_path / "vaultsh.toml"
    _write_config(config, networking=True, tor=True)

    def forbidden_client(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("direct connection must not occur if Tor is configured")

    monkeypatch.setattr("vaultsh.cli.BitcoinEsploraClient", forbidden_client)
    result = runner.invoke(
        app,
        [
            "bitcoin", "balance", ADDRESS,
            "--endpoint", "https://explorer.example/api",
            "--config", str(config), "--allow-network",
        ],
    )
    assert result.exit_code == 1
    assert "transport is" in result.stdout and "not implemented" in result.stdout


def test_balance_command_uses_explicit_endpoint_and_prints_exact_values(
    tmp_path: Path, monkeypatch: Any
) -> None:
    config = tmp_path / "vaultsh.toml"
    _write_config(config, networking=True)
    FakeBitcoinClient.calls.clear()
    monkeypatch.setattr("vaultsh.cli.BitcoinEsploraClient", FakeBitcoinClient)

    result = runner.invoke(
        app,
        [
            "bitcoin", "balance", ADDRESS,
            "--endpoint", "https://own-esplora.example/api",
            "--config", str(config), "--allow-network",
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert "Privacy notice" in result.stdout
    assert "1.23456789" in result.stdout
    assert "-0.00012345" in result.stdout
    assert "own-esplora.example" in result.stdout
    assert FakeBitcoinClient.calls == [
        ("https://own-esplora.example/api", "init", 2.0),
        ("https://own-esplora.example/api", ADDRESS, 2.0),
    ]
