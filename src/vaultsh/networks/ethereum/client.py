"""Read-only native-balance queries for explicit EVM profiles through JSON-RPC.

The adapter never selects a provider automatically, never sends transactions,
and requires the CLI to enforce the project's dual network-consent policy.
"""

from __future__ import annotations

import ipaddress
import json
import re
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from vaultsh.networks.base import NetworkError

MAX_RESPONSE_BYTES = 256_000
MAX_WEI = (1 << 256) - 1
_ADDRESS_PATTERN = re.compile(r"0x[0-9a-fA-F]{40}\Z")
_QUANTITY_PATTERN = re.compile(r"0x(?:0|[1-9a-fA-F][0-9a-fA-F]*)\Z")


@dataclass(frozen=True, slots=True)
class EvmNetworkProfile:
    """A small explicit allow-list of EVM mainnets and their native assets."""

    key: str
    name: str
    chain_id: int
    asset_symbol: str


EVM_NETWORKS: dict[str, EvmNetworkProfile] = {
    "ethereum": EvmNetworkProfile("ethereum", "Ethereum Mainnet", 1, "ETH"),
    "polygon": EvmNetworkProfile("polygon", "Polygon PoS Mainnet", 137, "POL"),
    "arbitrum": EvmNetworkProfile("arbitrum", "Arbitrum One", 42161, "ETH"),
    "optimism": EvmNetworkProfile("optimism", "Optimism Mainnet", 10, "ETH"),
    "base": EvmNetworkProfile("base", "Base Mainnet", 8453, "ETH"),
}


@dataclass(frozen=True, slots=True)
class EthereumAddressBalance:
    """Native balance on a supported EVM mainnet, represented in base units.

    ``balance_wei`` is retained as the original Ethereum-specific field name for
    compatibility. ``balance_base_units`` is the chain-neutral property and is
    the preferred name for consumers that handle more than Ethereum Mainnet.
    """

    address: str
    balance_wei: int
    chain_id: int = 1
    block_tag: str = "latest"
    network_name: str = "Ethereum Mainnet"
    asset_symbol: str = "ETH"

    @property
    def balance_base_units(self) -> int:
        """Return the balance in the selected network asset's smallest unit."""
        return self.balance_wei


def get_evm_network_profile(network: str) -> EvmNetworkProfile:
    """Return the explicit supported-chain profile or raise without guessing."""
    if not isinstance(network, str):
        raise NetworkError("EVM network must be one of the supported network names")
    try:
        return EVM_NETWORKS[network.strip().lower()]
    except KeyError as exc:
        choices = ", ".join(EVM_NETWORKS)
        raise NetworkError(f"Unsupported EVM network; choose one of: {choices}") from exc


def format_native_asset(base_units: int) -> str:
    """Format a native EVM asset with 18 decimals without floating-point math."""
    if (
        isinstance(base_units, bool)
        or not isinstance(base_units, int)
        or not 0 <= base_units <= MAX_WEI
    ):
        raise ValueError("base_units must be an unsigned 256-bit integer")
    whole, fractional = divmod(base_units, 10**18)
    if fractional == 0:
        return str(whole)
    fraction_text = f"{fractional:018d}".rstrip("0")
    return f"{whole}.{fraction_text}"


def format_eth(wei: int) -> str:
    """Format wei as an exact decimal ETH string without floating-point math."""
    return format_native_asset(wei)


def validate_ethereum_address(address: str) -> str:
    """Validate a 20-byte hex address and enforce EIP-55 for mixed-case inputs.

    All-lowercase and all-uppercase hexadecimal addresses are accepted. Mixed-case
    addresses must pass EIP-55 checksum validation using ``eth-utils``.
    """
    if not isinstance(address, str) or not _ADDRESS_PATTERN.fullmatch(address):
        raise NetworkError("Invalid EVM address: expected 0x plus 40 hexadecimal characters")
    body = address[2:]
    if body != body.lower() and body != body.upper():
        try:
            from eth_utils import is_checksum_address
        except ImportError as exc:
            raise NetworkError(
                "Mixed-case Ethereum address validation requires eth-utils; install project dependencies"
            ) from exc
        if not is_checksum_address(address):
            raise NetworkError("EVM address has an invalid EIP-55 checksum")
    return address


def validate_rpc_endpoint(endpoint: str) -> str:
    """Validate an explicit JSON-RPC URL before opening a connection.

    HTTPS is required for remote hosts. Plain HTTP is restricted to localhost
    and loopback addresses for self-hosted development nodes. URL credentials,
    query strings, fragments, and path dot-segments are rejected.
    """
    if not isinstance(endpoint, str) or not endpoint or len(endpoint) > 2048:
        raise NetworkError("An explicit, valid EVM JSON-RPC endpoint URL is required")
    if any(ord(char) < 32 or ord(char) == 127 for char in endpoint):
        raise NetworkError("Endpoint URL contains unsupported control characters")
    try:
        parsed = urlsplit(endpoint.strip())
        hostname = parsed.hostname
        _ = parsed.port
    except ValueError as exc:
        raise NetworkError("EVM JSON-RPC endpoint URL is malformed") from exc
    if parsed.scheme not in {"https", "http"} or not parsed.netloc or not hostname:
        raise NetworkError("Endpoint must be an absolute HTTPS URL (or loopback HTTP URL)")
    if parsed.username is not None or parsed.password is not None:
        raise NetworkError("Endpoint URLs must not include credentials")
    if parsed.query or parsed.fragment:
        raise NetworkError("Endpoint URLs must not include a query string or fragment")
    if any(segment in {".", ".."} for segment in unquote(parsed.path).split("/")):
        raise NetworkError("Endpoint URL path must not contain dot segments")

    loopback = hostname.casefold() == "localhost"
    try:
        loopback = loopback or ipaddress.ip_address(hostname).is_loopback
    except ValueError:
        pass
    if parsed.scheme == "http" and not loopback:
        raise NetworkError("Plain HTTP is allowed only for localhost or a loopback IP address")
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", ""))


class _NoRedirectHandler(HTTPRedirectHandler):
    """Disallow redirects so an explicit RPC endpoint cannot silently change hosts."""

    def redirect_request(
        self,
        req: Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        return None


class EvmJsonRpcClient:
    """Read-only EVM JSON-RPC client restricted to one selected network profile."""

    def __init__(
        self,
        endpoint: str,
        *,
        timeout_seconds: float = 15.0,
        opener: Any | None = None,
        max_response_bytes: int = MAX_RESPONSE_BYTES,
        expected_chain_id: int = 1,
        network_name: str = "Ethereum Mainnet",
        asset_symbol: str = "ETH",
    ) -> None:
        self.endpoint = validate_rpc_endpoint(endpoint)
        if isinstance(expected_chain_id, bool) or not isinstance(expected_chain_id, int) or expected_chain_id < 1:
            raise NetworkError("Expected chain ID must be a positive integer")
        if not network_name or not isinstance(network_name, str):
            raise NetworkError("Network name must be a non-empty string")
        if not asset_symbol or not isinstance(asset_symbol, str):
            raise NetworkError("Native asset symbol must be a non-empty string")
        self.expected_chain_id = expected_chain_id
        self.network_name = network_name
        self.asset_symbol = asset_symbol
        if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, (int, float)):
            raise NetworkError("Timeout must be a number")
        if not 0.1 <= timeout_seconds <= 300:
            raise NetworkError("Timeout must be between 0.1 and 300 seconds")
        if isinstance(max_response_bytes, bool) or not isinstance(max_response_bytes, int):
            raise NetworkError("Response size limit must be an integer")
        if not 1 <= max_response_bytes <= 10_000_000:
            raise NetworkError("Response size limit is outside the supported range")
        self.timeout_seconds = float(timeout_seconds)
        self.max_response_bytes = max_response_bytes
        # Deliberately ignore HTTP(S)_PROXY environment variables.
        self._opener = opener or build_opener(ProxyHandler({}), _NoRedirectHandler())

    def _rpc_call(self, method: str, params: list[Any], request_id: int) -> Any:
        body = json.dumps(
            {"jsonrpc": "2.0", "method": method, "params": params, "id": request_id},
            separators=(",", ":"),
        ).encode("utf-8")
        request = Request(
            self.endpoint,
            data=body,
            method="POST",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "Vaultsh/0.6.0",
            },
        )
        try:
            with self._opener.open(request, timeout=self.timeout_seconds) as response:
                raw = response.read(self.max_response_bytes + 1)
        except HTTPError as exc:
            if 300 <= exc.code < 400:
                raise NetworkError(
                    "EVM JSON-RPC endpoint returned a redirect; redirects are disabled for privacy"
                ) from exc
            raise NetworkError(f"EVM JSON-RPC request failed with HTTP status {exc.code}") from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise NetworkError("EVM JSON-RPC request failed; check endpoint and connection") from exc
        if len(raw) > self.max_response_bytes:
            raise NetworkError("EVM JSON-RPC response exceeded the configured size limit")
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise NetworkError("EVM JSON-RPC endpoint returned invalid JSON") from exc
        if not isinstance(payload, dict):
            raise NetworkError("EVM JSON-RPC returned an unexpected response format")
        response_id = payload.get("id")
        if payload.get("jsonrpc") != "2.0" or type(response_id) is not int or response_id != request_id:
            raise NetworkError("EVM JSON-RPC response did not match the request")
        if payload.get("error") is not None:
            # Do not echo provider-supplied error details; they may expose endpoint data.
            raise NetworkError("EVM JSON-RPC endpoint reported an error")
        if "result" not in payload:
            raise NetworkError("EVM JSON-RPC response is missing its result")
        return payload["result"]

    @staticmethod
    def _quantity(value: Any, *, field_name: str) -> int:
        if not isinstance(value, str) or not _QUANTITY_PATTERN.fullmatch(value):
            raise NetworkError(f"EVM JSON-RPC returned an invalid {field_name} quantity")
        result = int(value, 16)
        if not 0 <= result <= MAX_WEI:
            raise NetworkError(f"EVM JSON-RPC returned an out-of-range {field_name}")
        return result

    def get_address_balance(self, address: str) -> EthereumAddressBalance:
        """Verify the selected profile chain ID and fetch its latest native balance."""
        checked_address = validate_ethereum_address(address)
        chain_id = self._quantity(self._rpc_call("eth_chainId", [], 1), field_name="chain ID")
        if chain_id != self.expected_chain_id:
            raise NetworkError(
                f"Configured endpoint is not {self.network_name} (expected chain ID "
                f"{self.expected_chain_id}; got {chain_id})"
            )
        balance_wei = self._quantity(
            self._rpc_call("eth_getBalance", [checked_address, "latest"], 2),
            field_name="balance",
        )
        return EthereumAddressBalance(
            address=checked_address,
            balance_wei=balance_wei,
            chain_id=chain_id,
            network_name=self.network_name,
            asset_symbol=self.asset_symbol,
        )


# Compatibility alias for callers that used the earlier Ethereum-specific class name.
EthereumJsonRpcClient = EvmJsonRpcClient
