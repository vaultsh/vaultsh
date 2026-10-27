"""Configuration helpers for an optional local Tor SOCKS proxy.

This module does not start Tor, make requests, test reachability, or guarantee
anonymity. A compatible HTTP client must support SOCKS5 remote DNS (``socks5h``).
"""

from dataclasses import dataclass
import ipaddress


@dataclass(frozen=True, slots=True)
class TorSettings:
    """Settings for a Tor SOCKS listener, disabled unless explicitly enabled."""

    enabled: bool = False
    host: str = "127.0.0.1"
    port: int = 9050

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise ValueError("enabled must be a boolean")
        if (
            not isinstance(self.host, str)
            or not self.host
            or any(c in self.host for c in "/@?#")
        ):
            raise ValueError("host must be a hostname or IP address without URL syntax")
        if (
            not isinstance(self.port, int)
            or isinstance(self.port, bool)
            or not 1 <= self.port <= 65535
        ):
            raise ValueError("port must be between 1 and 65535")

    @property
    def proxy_url(self) -> str:
        """Return a SOCKS5 URL using remote DNS resolution."""
        host = self.host
        try:
            address = ipaddress.ip_address(host)
            if address.version == 6:
                host = f"[{host}]"
        except ValueError:
            if not host.replace("-", "").replace(".", "").isalnum():
                raise ValueError("host contains unsupported characters")
        return f"socks5h://{host}:{self.port}"

    def proxies(self) -> dict[str, str]:
        """Return HTTP client proxy settings, or fail when Tor is disabled."""
        if not self.enabled:
            raise RuntimeError("Tor proxy is disabled")
        url = self.proxy_url
        return {"http": url, "https": url}
