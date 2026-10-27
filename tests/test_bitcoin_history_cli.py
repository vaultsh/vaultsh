"""CLI tests for Bitcoin address history with no live network requests."""

from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from vaultsh.cli import app
from vaultsh.networks.bitcoin.client import BitcoinAddressTransaction

runner = CliRunner()
ADDRESS = "bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu"


def make_config(path: Path, *, network: bool, tor: bool = False) -> None:
    path.write_text(
        "[app]\n"
        f"network_requests_enabled = {'true' if network else 'false'}\n"
        f"tor_enabled = {'true' if tor else 'false'}\n"
        "request_timeout_seconds = 2.0\n",
        encoding="utf-8",
    )


class FakeHistoryClient:
    calls: list[tuple[Any, ...]] = []

    def __init__(self, endpoint: str, *, timeout_seconds: float) -> None:
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds
        type(self).calls.append(("init", endpoint, timeout_seconds))

    def get_address_transactions(
        self, address: str, *, limit: int = 10
    ) -> tuple[BitcoinAddressTransaction, ...]:
        type(self).calls.append(("history", address, limit))
        return (BitcoinAddressTransaction("a" * 64, True, 800_000, 1_700_000_000, 2500),)


def test_history_command_obeys_dual_opt_in(tmp_path: Path, monkeypatch: Any) -> None:
    config = tmp_path / "vaultsh.toml"
    make_config(config, network=True)
    monkeypatch.setattr(
        "vaultsh.cli.BitcoinEsploraClient",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("must not connect")),
    )
    result = runner.invoke(
        app,
        ["bitcoin", "history", ADDRESS, "--endpoint", "https://explorer.example/api",
         "--config", str(config), "--limit", "5"],
    )
    assert result.exit_code == 1
    assert "Network access is disabled" in result.stdout


def test_history_command_outputs_bounded_public_transaction_data(
    tmp_path: Path, monkeypatch: Any
) -> None:
    config = tmp_path / "vaultsh.toml"
    make_config(config, network=True)
    FakeHistoryClient.calls.clear()
    monkeypatch.setattr("vaultsh.cli.BitcoinEsploraClient", FakeHistoryClient)
    result = runner.invoke(
        app,
        ["bitcoin", "history", ADDRESS, "--endpoint", "https://explorer.example/api",
         "--config", str(config), "--allow-network", "--limit", "1"],
    )
    assert result.exit_code == 0, result.stdout
    assert "address transaction history" in result.stdout
    assert "Confirmed" in result.stdout
    assert "0.00002500" in result.stdout
    assert "not full wallet history" in result.stdout
    assert FakeHistoryClient.calls == [
        ("init", "https://explorer.example/api", 2.0),
        ("history", ADDRESS, 1),
    ]
