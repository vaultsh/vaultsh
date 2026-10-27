import pytest

from vaultsh.privacy.network_policy import (
    NetworkAccessDenied,
    may_connect,
    require_network_access,
    telemetry_enabled,
)


def test_telemetry_is_disabled() -> None:
    assert telemetry_enabled() is False


@pytest.mark.parametrize(
    ("requested", "configured", "expected"),
    [(False, False, False), (False, True, False), (True, False, False), (True, True, True)],
)
def test_network_requires_intent_and_configuration(
    requested: bool, configured: bool, expected: bool
) -> None:
    assert may_connect(explicitly_requested=requested, configured=configured) is expected


def test_network_policy_raises_unless_both_conditions_are_true() -> None:
    with pytest.raises(NetworkAccessDenied):
        require_network_access(explicitly_requested=True, configured=False)
    require_network_access(explicitly_requested=True, configured=True)
