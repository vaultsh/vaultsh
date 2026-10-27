from pathlib import Path

import pytest
from typer.testing import CliRunner

from vaultsh import __version__
from vaultsh.cli import app

runner = CliRunner()


def test_version_command() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert f"Vaultsh {__version__}" in result.stdout


def test_about_command_discloses_beta_status() -> None:
    result = runner.invoke(app, ["about"])
    assert result.exit_code == 0
    assert "beta" in result.stdout.lower()
    assert "not implemented" in result.stdout.lower()


def test_networks_command_shows_planned_networks() -> None:
    result = runner.invoke(app, ["networks"])
    assert result.exit_code == 0
    assert "Bitcoin" in result.stdout
    assert "Ethereum" in result.stdout
    assert "Monero" in result.stdout
    assert "Monero" in result.stdout and "monero-wallet-rpc" in result.stdout


def test_privacy_command_discloses_safe_defaults() -> None:
    result = runner.invoke(app, ["privacy"])
    assert result.exit_code == 0
    assert "Telemetry" in result.stdout
    assert "Disabled" in result.stdout
    assert "does not guarantee anonymity" in " ".join(result.stdout.split())


def test_config_command_shows_non_secret_defaults() -> None:
    result = runner.invoke(app, ["config"])
    assert result.exit_code == 0
    assert "network_requests_enabled" in result.stdout
    assert "false" in result.stdout


def test_no_arguments_shows_beta_warning() -> None:
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "VAULTSH" in result.stdout
    assert "BETA" in result.stdout
    assert "vault init" in result.stdout


def test_config_init_and_check(tmp_path: Path) -> None:
    path = tmp_path / "settings.toml"
    initialized = runner.invoke(app, ["config-init", str(path)])
    assert initialized.exit_code == 0
    assert path.exists()
    assert "Created config template" in initialized.stdout

    checked = runner.invoke(app, ["config-check", str(path)])
    assert checked.exit_code == 0
    assert "Configuration is valid" in checked.stdout
    assert "network_requests_enabled" in checked.stdout


def test_config_init_refuses_overwrite_by_default(tmp_path: Path) -> None:
    path = tmp_path / "settings.toml"
    path.write_text("keep", encoding="utf-8")
    result = runner.invoke(app, ["config-init", str(path)])
    assert result.exit_code == 1
    assert path.read_text(encoding="utf-8") == "keep"


def test_config_check_rejects_invalid_file(tmp_path: Path) -> None:
    path = tmp_path / "settings.toml"
    path.write_text("[app]\nunknown_option = true\n", encoding="utf-8")
    result = runner.invoke(app, ["config-check", str(path)])
    assert result.exit_code == 1
    assert "Invalid configuration" in result.stdout


def test_vault_init_and_check(tmp_path: Path) -> None:
    path = tmp_path / "main.vault"
    created = runner.invoke(
        app,
        ["vault", "init", str(path), "--label", "Test Vault"],
        input="correct-horse-battery\ncorrect-horse-battery\n",
    )
    assert created.exit_code == 0
    assert "Encrypted metadata container created" in created.stdout
    assert "does not create a blockchain wallet" in created.stdout

    checked = runner.invoke(app, ["vault", "check", str(path)], input="correct-horse-battery\n")
    assert checked.exit_code == 0
    assert "Test Vault" in checked.stdout
    assert "metadata schema validated" in checked.stdout


def test_vault_init_does_not_overwrite_existing_file(tmp_path: Path) -> None:
    path = tmp_path / "main.vault"
    path.write_bytes(b"keep")
    result = runner.invoke(
        app,
        ["vault", "init", str(path)],
        input="unused-password-value\nunused-password-value\n",
    )
    assert result.exit_code == 1
    assert path.read_bytes() == b"keep"


def test_vault_init_rejects_short_password(tmp_path: Path) -> None:
    path = tmp_path / "main.vault"
    result = runner.invoke(app, ["vault", "init", str(path)], input="short\nshort\n")
    assert result.exit_code == 1
    assert not path.exists()
    assert "at least 12 characters" in result.stdout


def test_vault_init_rejects_mismatched_passwords(tmp_path: Path) -> None:
    path = tmp_path / "main.vault"
    result = runner.invoke(
        app,
        ["vault", "init", str(path)],
        input="one-password-long\ntwo-password-long\n",
    )
    assert result.exit_code == 1
    assert not path.exists()
    assert "Passwords do not match" in result.stdout


def test_vault_backup_and_restore_commands(tmp_path: Path) -> None:
    vault_path = tmp_path / "main.vault"
    backup_path = tmp_path / "main.vault.backup"
    restored_path = tmp_path / "restored.vault"
    created = runner.invoke(
        app,
        ["vault", "init", str(vault_path)],
        input="correct-horse-battery\ncorrect-horse-battery\n",
    )
    assert created.exit_code == 0

    backed_up = runner.invoke(app, ["vault", "backup", str(vault_path), str(backup_path)])
    assert backed_up.exit_code == 0
    assert backup_path.read_bytes() == vault_path.read_bytes()

    restored = runner.invoke(app, ["vault", "restore", str(backup_path), str(restored_path)])
    assert restored.exit_code == 0
    assert restored_path.read_bytes() == vault_path.read_bytes()
    checked = runner.invoke(
        app, ["vault", "check", str(restored_path)], input="correct-horse-battery\n"
    )
    assert checked.exit_code == 0


def test_vault_check_rejects_wrong_password(tmp_path: Path) -> None:
    path = tmp_path / "main.vault"
    created = runner.invoke(
        app,
        ["vault", "init", str(path)],
        input="correct-horse-battery\ncorrect-horse-battery\n",
    )
    assert created.exit_code == 0
    checked = runner.invoke(app, ["vault", "check", str(path)], input="wrong-password-here\n")
    assert checked.exit_code == 1
    assert "Vault check failed" in checked.stdout


def test_vault_backup_does_not_overwrite_destination(tmp_path: Path) -> None:
    vault_path = tmp_path / "main.vault"
    destination = tmp_path / "backup.vault"
    runner.invoke(
        app,
        ["vault", "init", str(vault_path)],
        input="correct-horse-battery\ncorrect-horse-battery\n",
    )
    destination.write_bytes(b"keep")

    result = runner.invoke(app, ["vault", "backup", str(vault_path), str(destination)])
    assert result.exit_code == 1
    assert destination.read_bytes() == b"keep"


WALLET_TEST_PASSWORD = "test-only-password-phrase"
WALLET_TEST_MNEMONIC = (
    "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
)
WALLET_TEST_ADDRESS = "bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu"


def _patch_wallet_derivation(monkeypatch: pytest.MonkeyPatch) -> None:
    import vaultsh.storage.wallet_store as wallet_store
    from vaultsh.networks.bitcoin.wallet import DerivedBitcoinWallet

    monkeypatch.setattr(
        wallet_store,
        "derive_first_receive_address",
        lambda _: DerivedBitcoinWallet(
            mnemonic=WALLET_TEST_MNEMONIC,
            address=WALLET_TEST_ADDRESS,
        ),
    )


def test_wallet_create_list_and_explicit_recovery_phrase_flow(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from vaultsh.cli import app as cli_app
    from vaultsh.storage.wallet_store import list_wallets

    path = tmp_path / "main.vault"
    initialized = runner.invoke(
        cli_app,
        ["vault", "init", str(path)],
        input=f"{WALLET_TEST_PASSWORD}\n{WALLET_TEST_PASSWORD}\n",
    )
    assert initialized.exit_code == 0
    _patch_wallet_derivation(monkeypatch)
    monkeypatch.setattr(
        "vaultsh.cli.generate_mnemonic", lambda: WALLET_TEST_MNEMONIC
    )

    created = runner.invoke(
        cli_app,
        ["wallet", "create", "--vault", str(path), "--label", "Savings"],
        input=f"{WALLET_TEST_PASSWORD}\n",
    )
    assert created.exit_code == 0
    assert WALLET_TEST_ADDRESS in created.stdout
    assert all(word in created.stdout for word in WALLET_TEST_MNEMONIC.split())

    listed = runner.invoke(
        cli_app,
        ["wallet", "list", "--vault", str(path)],
        input=f"{WALLET_TEST_PASSWORD}\n",
    )
    assert listed.exit_code == 0
    assert "Savings" in listed.stdout
    assert "Recovery phrases are not shown" in listed.stdout
    assert WALLET_TEST_MNEMONIC not in listed.stdout

    wallet_id = list_wallets(path, WALLET_TEST_PASSWORD)[0].wallet_id
    revealed = runner.invoke(
        cli_app,
        ["wallet", "recovery-phrase", wallet_id, "--vault", str(path)],
        input=f"y\n{WALLET_TEST_PASSWORD}\n",
    )
    assert revealed.exit_code == 0
    assert all(word in revealed.stdout for word in WALLET_TEST_MNEMONIC.split())


def test_wallet_recovery_rejects_duplicate_address(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from vaultsh.cli import app as cli_app

    path = tmp_path / "main.vault"
    initialized = runner.invoke(
        cli_app,
        ["vault", "init", str(path)],
        input=f"{WALLET_TEST_PASSWORD}\n{WALLET_TEST_PASSWORD}\n",
    )
    assert initialized.exit_code == 0
    _patch_wallet_derivation(monkeypatch)

    first = runner.invoke(
        cli_app,
        ["wallet", "recover", "--vault", str(path), "--label", "First"],
        input=f"{WALLET_TEST_MNEMONIC}\n{WALLET_TEST_PASSWORD}\n",
    )
    assert first.exit_code == 0

    duplicate = runner.invoke(
        cli_app,
        ["wallet", "recover", "--vault", str(path), "--label", "Duplicate"],
        input=f"{WALLET_TEST_MNEMONIC}\n{WALLET_TEST_PASSWORD}\n",
    )
    assert duplicate.exit_code == 1
    assert "already present" in duplicate.stdout


def test_polish_dashboard_has_grouped_quickstart_and_language_hint() -> None:
    result = runner.invoke(app, ["--lang", "pl"])
    assert result.exit_code == 0
    assert "Przegląd poleceń" in result.stdout
    assert "Sugerowane pierwsze kroki" in result.stdout
    assert "vault init" in result.stdout
    assert "--allow-network" in result.stdout


def test_russian_about_command_is_localized() -> None:
    result = runner.invoke(app, ["--lang", "ru", "about"])
    assert result.exit_code == 0
    assert "О Vaultsh" in result.stdout
    assert "Ограничения" in result.stdout
    assert "необратимы" in result.stdout


def test_invalid_interface_language_fails_clearly() -> None:
    result = runner.invoke(app, ["--lang", "de"])
    assert result.exit_code == 2
    assert "Invalid interface language" in result.stdout


def test_polish_network_overview_localizes_evm_status() -> None:
    result = runner.invoke(app, ["--lang", "pl", "networks"])
    assert result.exit_code == 0
    assert "Przegląd obsługi sieci" in result.stdout
    assert "Saldo natywne" in result.stdout
    assert "portfel/adres/saldo/wysyłka" in result.stdout


def test_russian_privacy_screen_is_localized() -> None:
    result = runner.invoke(app, ["--lang", "ru", "privacy"])
    assert result.exit_code == 0
    assert "Конфиденциальность" in result.stdout
    assert "Телеметрия" in result.stdout
    assert "не гарантирует анонимность" in result.stdout


def test_textual_ui_commands_are_available_without_launching_tui() -> None:
    ui_help = runner.invoke(app, ["ui", "--help"])
    tui_help = runner.invoke(app, ["tui", "--help"])
    assert ui_help.exit_code == 0
    assert tui_help.exit_code == 0
    assert "Textual" in (ui_help.stdout + tui_help.stdout)
