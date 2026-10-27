"""Read-only Bitcoin address lookups against an explicitly chosen Esplora API.

This client does not use a default provider, follow redirects, read ambient proxy
settings, submit transactions, or access wallet secrets. Callers must separately
obtain permission through :mod:`vaultsh.privacy.network_policy` before connecting.
"""

from __future__ import annotations

import ipaddress
import json
import re
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from vaultsh.networks.base import NetworkError

MAX_RESPONSE_BYTES = 1_000_000
MAX_MONEY_SATS = 21_000_000 * 100_000_000
MAX_COUNTER_SATS = (1 << 127) - 1
_TXID_PATTERN = re.compile(r"[0-9a-fA-F]{64}\Z")


@dataclass(frozen=True, slots=True)
class BitcoinAddressTransaction:
    """A validated public transaction summary returned by Esplora."""

    txid: str
    confirmed: bool
    block_height: int | None
    block_time: int | None
    fee_sats: int | None


@dataclass(frozen=True, slots=True)
class BitcoinAddressBalance:
    """Address balance totals, represented exactly in satoshis."""

    address: str
    confirmed_sats: int
    unconfirmed_sats: int

    @property
    def estimated_total_sats(self) -> int:
        """Confirmed value plus the net effect of unconfirmed transactions."""
        return self.confirmed_sats + self.unconfirmed_sats


def format_btc(satoshis: int) -> str:
    """Format satoshis as an exact eight-decimal BTC string without floats."""
    sign = "-" if satoshis < 0 else ""
    whole, fractional = divmod(abs(satoshis), 100_000_000)
    return f"{sign}{whole}.{fractional:08d}"


def validate_esplora_endpoint(endpoint: str) -> str:
    """Validate and normalize a base URL before any network activity.

    HTTPS is required for remote hosts. Plain HTTP is accepted only for localhost
    or an IP address explicitly identified as loopback, supporting a local
    self-hosted Esplora instance without permitting remote cleartext endpoints.
    Credentials, query strings, fragments, and URL control characters are rejected.
    """
    if not isinstance(endpoint, str) or not endpoint or len(endpoint) > 2048:
        raise NetworkError("An explicit, valid Esplora endpoint URL is required")
    if any(ord(char) < 32 or ord(char) == 127 for char in endpoint):
        raise NetworkError("Endpoint URL contains unsupported control characters")

    try:
        parsed = urlsplit(endpoint.strip())
        hostname = parsed.hostname
        # Accessing .port raises ValueError for malformed ports.
        _ = parsed.port
    except ValueError as exc:
        raise NetworkError("Endpoint URL is malformed") from exc

    if parsed.scheme not in {"https", "http"} or not parsed.netloc or not hostname:
        raise NetworkError("Endpoint must be an absolute HTTPS URL (or local loopback HTTP URL)")
    if parsed.username is not None or parsed.password is not None:
        raise NetworkError("Endpoint URLs must not include credentials")
    if parsed.query or parsed.fragment:
        raise NetworkError("Endpoint URLs must not include a query string or fragment")

    # Avoid confusing encoded traversal components in reverse-proxy prefixes.
    path_segments = unquote(parsed.path).split("/")
    if any(segment in {".", ".."} for segment in path_segments):
        raise NetworkError("Endpoint URL path must not contain dot segments")

    loopback = hostname.casefold() == "localhost"
    try:
        loopback = loopback or ipaddress.ip_address(hostname).is_loopback
    except ValueError:
        pass
    if parsed.scheme == "http" and not loopback:
        raise NetworkError("Plain HTTP is allowed only for localhost or a loopback IP address")

    # Ensure endpoint paths are preserved while dropping query/fragment (already rejected).
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", ""))


def _validate_mainnet_address(address: str) -> None:
    """Validate a supported Bitcoin Mainnet address using ``embit``."""
    if not isinstance(address, str) or not 14 <= len(address) <= 90:
        raise NetworkError("Invalid Bitcoin Mainnet address")
    # Restrict to prefixes used by standard mainnet address encodings before parsing.
    is_legacy_mainnet = address.startswith(("1", "3"))
    is_segwit_mainnet = address.casefold().startswith(("bc1q", "bc1p"))
    if not (is_legacy_mainnet or is_segwit_mainnet):
        raise NetworkError("Only Bitcoin Mainnet addresses are supported")
    try:
        from embit.script import address_to_scriptpubkey
    except ImportError as exc:
        raise NetworkError(
            "Bitcoin address validation requires embit; install project dependencies and retry"
        ) from exc
    try:
        address_to_scriptpubkey(address)
    except Exception as exc:
        # Keep input text out of error messages; the input may be private or malformed.
        raise NetworkError("Invalid Bitcoin Mainnet address or checksum") from exc


def _stat_balance(stats: Any, *, field_name: str) -> int:
    if not isinstance(stats, dict):
        raise NetworkError(f"Esplora response is missing valid {field_name} statistics")
    funded = stats.get("funded_txo_sum")
    spent = stats.get("spent_txo_sum")
    if (
        isinstance(funded, bool)
        or not isinstance(funded, int)
        or isinstance(spent, bool)
        or not isinstance(spent, int)
        or not 0 <= funded <= MAX_COUNTER_SATS
        or not 0 <= spent <= MAX_COUNTER_SATS
    ):
        raise NetworkError(f"Esplora response has invalid {field_name} satoshi values")
    # funded_txo_sum/spent_txo_sum are cumulative lifetime counters, so they can
    # exceed the 21-million-BTC supply when an address is reused many times. The
    # net current balance, unlike those cumulative counters, is supply-bounded.
    balance = funded - spent
    if field_name == "confirmed" and not 0 <= balance <= MAX_MONEY_SATS:
        raise NetworkError("Esplora response has an impossible confirmed balance")
    if field_name == "unconfirmed" and not -MAX_MONEY_SATS <= balance <= MAX_MONEY_SATS:
        raise NetworkError("Esplora response has an impossible unconfirmed balance change")
    return balance


class _NoRedirectHandler(HTTPRedirectHandler):
    """Disallow redirects so an explicit endpoint cannot silently change hosts."""

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


class BitcoinEsploraClient:
    """Small, read-only Esplora client for Bitcoin Mainnet address statistics.

    No endpoint is selected automatically. This class does not itself determine
    whether the user authorized network access; the CLI must enforce that policy.
    """

    def __init__(
        self,
        endpoint: str,
        *,
        timeout_seconds: float = 15.0,
        opener: Any | None = None,
        max_response_bytes: int = MAX_RESPONSE_BYTES,
    ) -> None:
        self.endpoint = validate_esplora_endpoint(endpoint)
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
        # Ignore HTTP(S)_PROXY environment variables to avoid invisible proxy routing.
        self._opener = opener or build_opener(ProxyHandler({}), _NoRedirectHandler())

    def get_address_balance(self, address: str) -> BitcoinAddressBalance:
        """Fetch confirmed and net-unconfirmed value for one Mainnet address."""
        _validate_mainnet_address(address)
        path_address = quote(address, safe="")
        url = f"{self.endpoint}/address/{path_address}"
        request = Request(
            url,
            method="GET",
            headers={
                "Accept": "application/json",
                "User-Agent": "Vaultsh/1.0.0b1",
            },
        )
        try:
            with self._opener.open(request, timeout=self.timeout_seconds) as response:
                raw = response.read(self.max_response_bytes + 1)
        except HTTPError as exc:
            if 300 <= exc.code < 400:
                raise NetworkError(
                    "Esplora endpoint returned a redirect; redirects are disabled for privacy"
                ) from exc
            raise NetworkError(f"Esplora request failed with HTTP status {exc.code}") from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise NetworkError(
                "Esplora request failed; check the endpoint and network connection"
            ) from exc

        if len(raw) > self.max_response_bytes:
            raise NetworkError("Esplora response exceeded the configured size limit")
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise NetworkError("Esplora endpoint returned invalid JSON") from exc
        if not isinstance(payload, dict):
            raise NetworkError("Esplora endpoint returned an unexpected response format")

        response_address = payload.get("address")
        if not isinstance(response_address, str):
            raise NetworkError("Esplora response is missing its address field")
        same_address = response_address == address
        if address.casefold().startswith("bc1"):
            same_address = response_address.casefold() == address.casefold()
        if not same_address:
            raise NetworkError("Esplora response address did not match the requested address")

        confirmed = _stat_balance(payload.get("chain_stats"), field_name="confirmed")
        unconfirmed = _stat_balance(payload.get("mempool_stats"), field_name="unconfirmed")
        estimated_total = confirmed + unconfirmed
        if not 0 <= estimated_total <= MAX_MONEY_SATS:
            raise NetworkError("Esplora response yields an impossible estimated balance")
        return BitcoinAddressBalance(
            address=address,
            confirmed_sats=confirmed,
            unconfirmed_sats=unconfirmed,
        )


    def get_address_transactions(
        self, address: str, *, limit: int = 10
    ) -> tuple[BitcoinAddressTransaction, ...]:
        """Fetch a bounded, newest-first transaction summary for one Mainnet address.

        This is address-scoped history, not a complete wallet history. Esplora's
        address endpoint has pagination and result limits; this method returns at
        most ``limit`` entries from the first response page.
        """
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 25:
            raise NetworkError("Transaction history limit must be an integer from 1 to 25")
        _validate_mainnet_address(address)
        path_address = quote(address, safe="")
        url = f"{self.endpoint}/address/{path_address}/txs"
        request = Request(
            url,
            method="GET",
            headers={"Accept": "application/json", "User-Agent": "Vaultsh/1.0.0b1"},
        )
        try:
            with self._opener.open(request, timeout=self.timeout_seconds) as response:
                raw = response.read(self.max_response_bytes + 1)
        except HTTPError as exc:
            if 300 <= exc.code < 400:
                raise NetworkError(
                    "Esplora endpoint returned a redirect; redirects are disabled for privacy"
                ) from exc
            raise NetworkError(f"Esplora request failed with HTTP status {exc.code}") from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise NetworkError(
                "Esplora request failed; check the endpoint and network connection"
            ) from exc
        if len(raw) > self.max_response_bytes:
            raise NetworkError("Esplora response exceeded the configured size limit")
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise NetworkError("Esplora endpoint returned invalid JSON") from exc
        if not isinstance(payload, list):
            raise NetworkError("Esplora transaction endpoint returned an unexpected format")
        if len(payload) > 1000:
            raise NetworkError("Esplora transaction response contains too many entries")

        transactions: list[BitcoinAddressTransaction] = []
        seen_txids: set[str] = set()
        for item in payload[:limit]:
            if not isinstance(item, dict):
                raise NetworkError("Esplora transaction entry must be an object")
            txid = item.get("txid")
            if not isinstance(txid, str) or not _TXID_PATTERN.fullmatch(txid):
                raise NetworkError("Esplora transaction entry has an invalid transaction ID")
            txid = txid.lower()
            if txid in seen_txids:
                raise NetworkError("Esplora transaction response contains duplicate transaction IDs")
            seen_txids.add(txid)
            status = item.get("status")
            if not isinstance(status, dict) or not isinstance(status.get("confirmed"), bool):
                raise NetworkError("Esplora transaction entry has an invalid status")
            confirmed = status["confirmed"]
            block_height: int | None = None
            block_time: int | None = None
            if confirmed:
                height = status.get("block_height")
                timestamp = status.get("block_time")
                if (
                    isinstance(height, bool) or not isinstance(height, int) or height < 0
                    or isinstance(timestamp, bool) or not isinstance(timestamp, int) or timestamp < 0
                ):
                    raise NetworkError("Confirmed transaction is missing valid block metadata")
                block_height, block_time = height, timestamp
            fee = item.get("fee")
            if fee is not None and (
                isinstance(fee, bool) or not isinstance(fee, int) or not 0 <= fee <= MAX_MONEY_SATS
            ):
                raise NetworkError("Esplora transaction entry has an invalid fee")
            transactions.append(
                BitcoinAddressTransaction(
                    txid=txid,
                    confirmed=confirmed,
                    block_height=block_height,
                    block_time=block_time,
                    fee_sats=fee,
                )
            )
        return tuple(transactions)
