"""Validated, non-secret application configuration.

Only operational preferences belong here. Never put passwords, private keys,
seed phrases, recovery words, or derived encryption keys in a config file.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ConfigError(ValueError):
    """Raised when a configuration file or setting is invalid."""


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Non-secret settings with privacy-preserving defaults."""

    app_name: str = "vaultsh"
    telemetry_enabled: bool = False
    network_requests_enabled: bool = False
    tor_enabled: bool = False
    request_timeout_seconds: float = 15.0

    def __post_init__(self) -> None:
        if (
            not isinstance(self.app_name, str)
            or not self.app_name
            or self.app_name.strip() != self.app_name
        ):
            raise ConfigError("app_name must be a non-empty string without surrounding whitespace")
        if not isinstance(self.telemetry_enabled, bool):
            raise ConfigError("telemetry_enabled must be a boolean")
        if not isinstance(self.network_requests_enabled, bool):
            raise ConfigError("network_requests_enabled must be a boolean")
        if not isinstance(self.tor_enabled, bool):
            raise ConfigError("tor_enabled must be a boolean")
        if isinstance(self.request_timeout_seconds, bool) or not isinstance(
            self.request_timeout_seconds, (int, float)
        ):
            raise ConfigError("request_timeout_seconds must be a number")
        if not 0.1 <= self.request_timeout_seconds <= 300:
            raise ConfigError("request_timeout_seconds must be between 0.1 and 300 seconds")
        if self.tor_enabled and not self.network_requests_enabled:
            # Tor is a transport setting, not a way to implicitly enable networking.
            raise ConfigError("tor_enabled requires network_requests_enabled=True")


def _expect_bool(data: dict[str, Any], name: str, default: bool) -> bool:
    value = data.get(name, default)
    if not isinstance(value, bool):
        raise ConfigError(f"{name} must be a TOML boolean")
    return value


def load_config(path: str | Path) -> AppConfig:
    """Load an ``[app]`` table from TOML and validate all recognized fields.

    Unknown keys are rejected so spelling mistakes do not silently change
    privacy- or network-related behavior.
    """
    config_path = Path(path)
    try:
        with config_path.open("rb") as stream:
            raw = tomllib.load(stream)
    except FileNotFoundError:
        raise
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ConfigError(f"Could not read config: {exc}") from exc

    if set(raw) - {"app"}:
        unexpected = ", ".join(sorted(set(raw) - {"app"}))
        raise ConfigError(f"Unknown top-level config section(s): {unexpected}")
    section = raw.get("app", {})
    if not isinstance(section, dict):
        raise ConfigError("[app] must be a TOML table")

    allowed = {
        "app_name",
        "telemetry_enabled",
        "network_requests_enabled",
        "tor_enabled",
        "request_timeout_seconds",
    }
    unknown = set(section) - allowed
    if unknown:
        raise ConfigError(f"Unknown [app] key(s): {', '.join(sorted(unknown))}")

    app_name = section.get("app_name", "vaultsh")
    if not isinstance(app_name, str):
        raise ConfigError("app_name must be a string")

    timeout = section.get("request_timeout_seconds", 15.0)
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
        raise ConfigError("request_timeout_seconds must be a number")

    return AppConfig(
        app_name=app_name,
        telemetry_enabled=_expect_bool(section, "telemetry_enabled", False),
        network_requests_enabled=_expect_bool(section, "network_requests_enabled", False),
        tor_enabled=_expect_bool(section, "tor_enabled", False),
        request_timeout_seconds=float(timeout),
    )
