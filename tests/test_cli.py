from typer.testing import CliRunner

from vaultsh.cli import app

runner = CliRunner()


def test_version_command() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "Vaultsh" in result.stdout


def test_about_command_discloses_pre_alpha_status() -> None:
    result = runner.invoke(app, ["about"])
    assert result.exit_code == 0
    assert "pre-alpha" in result.stdout.lower()
    assert "not implemented" in result.stdout.lower()


def test_networks_command_shows_planned_networks() -> None:
    result = runner.invoke(app, ["networks"])
    assert result.exit_code == 0
    assert "Bitcoin" in result.stdout
    assert "Ethereum" in result.stdout
    assert "Monero" in result.stdout
    assert "not implemented" in result.stdout.lower()


def test_privacy_command_discloses_safe_defaults() -> None:
    result = runner.invoke(app, ["privacy"])
    assert result.exit_code == 0
    assert "Telemetry" in result.stdout
    assert "Disabled" in result.stdout
    assert "does not guarantee anonymity" in result.stdout


def test_config_command_shows_non_secret_defaults() -> None:
    result = runner.invoke(app, ["config"])
    assert result.exit_code == 0
    assert "network_requests_enabled" in result.stdout
    assert "false" in result.stdout


def test_no_arguments_shows_pre_alpha_warning() -> None:
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "VAULTSH" in result.stdout
    assert "PRE-ALPHA" in result.stdout
