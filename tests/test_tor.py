import pytest

from vaultsh.privacy.tor import TorSettings


def test_tor_is_disabled_by_default() -> None:
    settings = TorSettings()
    assert settings.enabled is False
    with pytest.raises(RuntimeError, match="disabled"):
        settings.proxies()


def test_enabled_tor_settings_use_socks5_remote_dns() -> None:
    settings = TorSettings(enabled=True)
    assert settings.proxy_url == "socks5h://127.0.0.1:9050"
    assert settings.proxies() == {
        "http": "socks5h://127.0.0.1:9050",
        "https": "socks5h://127.0.0.1:9050",
    }


def test_ipv6_proxy_host_is_bracketed() -> None:
    assert TorSettings(host="::1").proxy_url == "socks5h://[::1]:9050"


@pytest.mark.parametrize("port", [0, -1, 65536, True])
def test_invalid_port_is_rejected(port: int) -> None:
    with pytest.raises(ValueError, match="port"):
        TorSettings(port=port)
