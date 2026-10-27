"""Explicit, privacy-preserving policy helpers for future network clients."""


class NetworkAccessDenied(PermissionError):
    """Raised when an outbound request is not explicitly allowed."""


def telemetry_enabled() -> bool:
    """Vaultsh telemetry is intentionally disabled in this build."""
    return False


def may_connect(*, explicitly_requested: bool, configured: bool) -> bool:
    """Return whether an outbound connection has both required permissions."""
    return explicitly_requested is True and configured is True


def require_network_access(*, explicitly_requested: bool, configured: bool) -> None:
    """Raise unless both the user's intent and app configuration permit access."""
    if not may_connect(explicitly_requested=explicitly_requested, configured=configured):
        raise NetworkAccessDenied(
            "Network access is disabled: request it explicitly and enable it in configuration"
        )
