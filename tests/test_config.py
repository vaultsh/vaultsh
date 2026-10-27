from pathlib import Path

import pytest

from vaultsh.config import AppConfig, ConfigError, load_config


def test_privacy_defaults() -> None:
    config = AppConfig()
    assert config.telemetry_enabled is False
    assert config.network_requests_enabled is False
    assert config.tor_enabled is False
    assert config.request_timeout_seconds == 15.0


def test_config_is_immutable() -> None:
    config = AppConfig()
    with pytest.raises((AttributeError, TypeError)):
        config.telemetry_enabled = True  # type: ignore[misc]


def test_invalid_timeout_is_rejected() -> None:
    with pytest.raises(ConfigError):
        AppConfig(request_timeout_seconds=0)
    with pytest.raises(ConfigError):
        AppConfig(request_timeout_seconds=301)


def test_tor_requires_networking_to_be_enabled() -> None:
    with pytest.raises(ConfigError, match="requires network_requests_enabled"):
        AppConfig(tor_enabled=True)


def test_load_config_from_toml(tmp_path: Path) -> None:
    path = tmp_path / "config.toml"
    path.write_text(
        "[app]\napp_name = 'vaultsh-test'\nnetwork_requests_enabled = true\n"
        "request_timeout_seconds = 20.5\n",
        encoding="utf-8",
    )

    config = load_config(path)
    assert config.app_name == "vaultsh-test"
    assert config.network_requests_enabled is True
    assert config.telemetry_enabled is False
    assert config.request_timeout_seconds == 20.5


def test_load_config_rejects_unknown_keys(tmp_path: Path) -> None:
    path = tmp_path / "config.toml"
    path.write_text("[app]\nnetwrok_requests_enabled = true\n", encoding="utf-8")
    with pytest.raises(ConfigError, match=r"Unknown \[app\] key"):
        load_config(path)


def test_load_config_rejects_wrong_types(tmp_path: Path) -> None:
    path = tmp_path / "config.toml"
    path.write_text("[app]\ntelemetry_enabled = 'yes'\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="telemetry_enabled must be a TOML boolean"):
        load_config(path)
