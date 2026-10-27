from vaultsh.ui.tui_helpers import safe_username, window_title


def test_title_includes_version_user_and_network_state() -> None:
    title = window_title("alice", "REQUESTING")
    assert title.startswith("Vaultsh v1.0.0b1 | alice | NET REQUESTING")


def test_title_sanitizes_control_characters() -> None:
    title = window_title("alice\n\x1b[31m", "armed\x1b[0m")
    assert "\n" not in title
    assert "\x1b" not in title
    assert "NET ARMED" in title


def test_username_is_short_and_printable() -> None:
    username = safe_username("ab\ncd/ef" + "x" * 100)
    assert len(username) <= 32
    assert all(character.isalnum() or character in "._- " for character in username)
    assert safe_username("\n///") == "user"
