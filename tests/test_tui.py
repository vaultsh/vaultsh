"""Headless Textual UI regression tests (run when the Textual dependency is installed)."""

from __future__ import annotations

import pytest

textual = pytest.importorskip("textual", reason="Textual UI tests require the project dependency")

from vaultsh.ui.tui import VaultshApp, safe_username, window_title  # noqa: E402


@pytest.mark.parametrize("language", ["en", "pl", "ru"])
async def test_tui_mounts_all_primary_tabs(language: str, tmp_path) -> None:
    app = VaultshApp(language=language, config_path=tmp_path / "missing.toml")
    async with app.run_test(size=(120, 45)) as pilot:
        assert app.query_one("#overview")
        assert app.query_one("#wallet")
        assert app.query_one("#network")
        assert app.query_one("#files")
        assert app.query_one("#settings")
        assert app.query_one("#overview-network-table")
        assert app.query_one("#version-digits")
        assert app.query_one("#network-chain")
        assert app.query_one("#network-consent")
        assert app.query_one("#file-tree")
        assert app.query_one("#use-selected-vault-path")
        assert app.title.startswith("Vaultsh v0.9.0")
        assert "NET OFF" in app.title
        await pilot.press("ctrl+r")
        await pilot.pause()
        assert "NET OFF" in app.title
        app._network_state = "REQUESTING"
        app._update_network_indicator()
        assert "NET REQUESTING" in app.title


async def test_tui_settings_are_network_off_by_default(tmp_path) -> None:
    app = VaultshApp(language="en", config_path=tmp_path / "missing.toml")
    async with app.run_test(size=(100, 40)) as pilot:
        network_toggle = app.query_one("#settings-network-enabled")
        assert network_toggle.value is False
        assert app.query_one("#network-consent").value is False
        # The preference and the one-shot query consent are separate gates.
        # Loading the app never starts a request automatically.
        assert app._network_state == "OFF"
        assert app._network_request_in_progress is False


def test_terminal_title_sanitizes_username_and_state() -> None:
    title = window_title("user\n[red]alice", "requesting\x1b")
    assert "\n" not in title
    assert "\x1b" not in title
    assert "NET REQUESTING" in title


def test_safe_username_is_printable() -> None:
    username = safe_username()
    assert username
    assert all(char.isalnum() or char in "._- " for char in username)
