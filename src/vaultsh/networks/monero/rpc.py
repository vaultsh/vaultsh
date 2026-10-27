"""Thin, loopback-only bridge to the official monero-wallet-rpc.

Vaultsh does not implement Monero key derivation itself. The official Monero wallet
process owns the Monero wallet file, seed handling, transaction construction and
signing. This adapter performs explicit JSON-RPC calls to a local wallet service.
"""
from __future__ import annotations

import ipaddress
import json
import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import HTTPDigestAuthHandler, HTTPPasswordMgrWithDefaultRealm, HTTPRedirectHandler, ProxyHandler, Request, build_opener

from vaultsh.networks.base import NetworkError

ATOMIC_UNITS = 10**12
MAX_XMR_ATOMIC = 18_446_744_073_709_551_615


@dataclass(frozen=True, slots=True)
class MoneroTransferPreview:
    destination: str
    amount_atomic: int
    fee_atomic: int
    tx_hash: str
    tx_metadata: str = field(repr=False)



def xmr_to_atomic(amount: str) -> int:
    if not isinstance(amount, str) or not amount.strip() or len(amount) > 80:
        raise NetworkError("XMR amount must be a positive decimal string")
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", amount.strip()):
        raise NetworkError("XMR amount must use plain decimal notation")
    try:
        value = Decimal(amount.strip())
    except InvalidOperation as exc:
        raise NetworkError("XMR amount is invalid") from exc
    if not value.is_finite() or value <= 0 or value.as_tuple().exponent < -12:
        raise NetworkError("XMR amount must be positive and have at most 12 decimal places")
    atomic = value * ATOMIC_UNITS
    if atomic != atomic.to_integral_value() or int(atomic) > MAX_XMR_ATOMIC:
        raise NetworkError("XMR amount is outside the supported range")
    return int(atomic)


def format_xmr(amount_atomic: int) -> str:
    if isinstance(amount_atomic, bool) or not isinstance(amount_atomic, int) or not 0 <= amount_atomic <= MAX_XMR_ATOMIC:
        raise NetworkError("Invalid atomic XMR amount")
    whole, frac = divmod(amount_atomic, ATOMIC_UNITS)
    return f"{whole}.{frac:012d}".rstrip("0").rstrip(".") if frac else str(whole)


class MoneroWalletRpcClient:
    """Connect only to local monero-wallet-rpc; remote hosts are deliberately rejected."""

    def __init__(self, endpoint: str = "http://127.0.0.1:18082/json_rpc", *, timeout_seconds: float = 15.0,
                 username: str | None = None, password: str | None = None, opener: Any | None = None):
        parsed_endpoint = self._validate_local_endpoint(endpoint)
        if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, (int, float)) or not 0.1 <= timeout_seconds <= 300:
            raise NetworkError("Timeout must be between 0.1 and 300 seconds")
        self.endpoint = parsed_endpoint
        self.timeout_seconds = float(timeout_seconds)
        if opener is not None:
            self._opener = opener
        else:
            handlers: list[Any] = [ProxyHandler({}), _NoRedirectHandler()]
            if username is not None or password is not None:
                if not username or not password:
                    raise NetworkError("Monero RPC username and password must both be set")
                manager = HTTPPasswordMgrWithDefaultRealm()
                manager.add_password(None, parsed_endpoint, username, password)
                handlers.append(HTTPDigestAuthHandler(manager))
            self._opener = build_opener(*handlers)

    @staticmethod
    def _validate_local_endpoint(endpoint: str) -> str:
        if not isinstance(endpoint, str) or len(endpoint) > 512:
            raise NetworkError("A local Monero wallet RPC URL is required")
        try:
            parsed = urlsplit(endpoint.strip())
            hostname = parsed.hostname
            _ = parsed.port
        except ValueError as exc:
            raise NetworkError("Monero RPC URL is malformed") from exc
        if parsed.scheme != "http" or not parsed.netloc or not hostname:
            raise NetworkError("Monero wallet RPC must use local HTTP, not a remote endpoint")
        if parsed.username is not None or parsed.password is not None or parsed.query or parsed.fragment:
            raise NetworkError("Monero RPC URL must not include credentials, query or fragment")
        loopback = hostname.casefold() == "localhost"
        try:
            loopback = loopback or ipaddress.ip_address(hostname).is_loopback
        except ValueError:
            pass
        if not loopback:
            raise NetworkError("Monero wallet RPC is restricted to localhost/loopback")
        if parsed.path not in {"", "/", "/json_rpc"}:
            raise NetworkError("Monero wallet RPC path must be /json_rpc")
        return urlunsplit(("http", parsed.netloc, "/json_rpc", "", ""))

    def call(self, method: str, params: dict[str, Any] | None = None, *, request_id: str = "vaultsh") -> dict[str, Any]:
        body = json.dumps({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params or {}}, separators=(",", ":")).encode()
        request = Request(self.endpoint, data=body, method="POST", headers={"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "Vaultsh/1.0.0b1"})
        try:
            with self._opener.open(request, timeout=self.timeout_seconds) as response:
                raw = response.read(1_000_001)
        except HTTPError as exc:
            if 300 <= exc.code < 400:
                raise NetworkError("Monero RPC redirects are blocked") from exc
            raise NetworkError(f"Monero RPC returned HTTP status {exc.code}") from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise NetworkError("Could not connect to local monero-wallet-rpc") from exc
        if len(raw) > 1_000_000:
            raise NetworkError("Monero RPC response exceeded the configured size limit")
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise NetworkError("Monero RPC returned invalid JSON") from exc
        if not isinstance(payload, dict) or payload.get("id") != request_id:
            raise NetworkError("Monero RPC response did not match the request")
        if payload.get("error") is not None:
            # Do not echo daemon-provided messages into the terminal; they may contain sensitive details.
            raise NetworkError(f"Monero wallet RPC method {method} failed")
        result = payload.get("result")
        if not isinstance(result, dict):
            raise NetworkError("Monero wallet RPC result has an unexpected format")
        return result

    @staticmethod
    def _validate_wallet_name(filename: str) -> str:
        if not isinstance(filename, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", filename):
            raise NetworkError("Monero wallet name must be a simple filename (letters, digits, dot, underscore, hyphen)")
        if filename in {".", ".."} or ".." in filename:
            raise NetworkError("Monero wallet name must not contain path traversal")
        return filename

    def create_wallet(self, filename: str, password: str, *, language: str = "English") -> None:
        """Create a wallet file managed by the local official Monero RPC process."""
        name = self._validate_wallet_name(filename)
        if not isinstance(password, str) or len(password) < 1 or len(password) > 1024:
            raise NetworkError("A non-empty Monero wallet password is required")
        if language != "English":
            raise NetworkError("This release currently creates Monero wallets with English seed words only")
        self.call("create_wallet", {"filename": name, "password": password, "language": language}, request_id="create-wallet")

    def open_wallet(self, filename: str, password: str) -> None:
        """Open an existing Monero wallet from the local RPC wallet directory."""
        name = self._validate_wallet_name(filename)
        if not isinstance(password, str) or len(password) > 1024:
            raise NetworkError("Monero wallet password is invalid")
        self.call("open_wallet", {"filename": name, "password": password}, request_id="open-wallet")

    def close_wallet(self) -> None:
        """Close the currently opened Monero wallet via the local RPC process."""
        self.call("close_wallet", {}, request_id="close-wallet")

    def _validate_mainnet_address(self, address: str) -> str:
        """Ask the wallet RPC to validate a public address and require Mainnet."""
        if not isinstance(address, str) or len(address) not in {95, 106} or not address.isascii():
            raise NetworkError("Monero wallet RPC returned an invalid address")
        check = self.call(
            "validate_address", {"address": address, "any_net_type": True},
            request_id="validate-monero-address",
        )
        nettype = check.get("nettype")
        if check.get("valid") is not True or not isinstance(nettype, str) or nettype.casefold() != "mainnet":
            raise NetworkError("Monero wallet RPC address is not a valid Monero Mainnet address")
        return address

    def get_address(self, account_index: int = 0) -> str:
        result = self.call("get_address", {"account_index": account_index})
        addresses = result.get("addresses")
        if not isinstance(addresses, list) or not addresses or not isinstance(addresses[0], dict):
            raise NetworkError("Monero wallet RPC returned no address")
        address = addresses[0].get("address")
        return self._validate_mainnet_address(address)

    def get_balance(self, account_index: int = 0) -> tuple[int, int]:
        # Refuse a wallet RPC process that is configured against testnet/stagenet.
        # This also verifies that a wallet is actually open before reading balances.
        self.get_address(account_index)
        result = self.call("get_balance", {"account_index": account_index})
        balance, unlocked = result.get("balance"), result.get("unlocked_balance")
        if any(isinstance(x, bool) or not isinstance(x, int) or not 0 <= x <= MAX_XMR_ATOMIC for x in (balance, unlocked)):
            raise NetworkError("Monero wallet RPC returned invalid balance values")
        return balance, unlocked

    def prepare_transfer(self, *, destination: str, amount: str, account_index: int = 0, priority: int = 2) -> MoneroTransferPreview:
        amount_atomic = xmr_to_atomic(amount)
        if not isinstance(destination, str) or not 90 <= len(destination) <= 110 or not destination.isascii():
            raise NetworkError("Monero destination address length is invalid")
        if isinstance(priority, bool) or not isinstance(priority, int) or priority not in {0, 1, 2, 3, 4}:
            raise NetworkError("Monero fee priority must be from 0 to 4")
        validation = self.call("validate_address", {"address": destination, "any_net_type": False}, request_id="validate")
        nettype = validation.get("nettype")
        if validation.get("valid") is not True or not isinstance(nettype, str) or nettype.lower() != "mainnet":
            raise NetworkError("Destination is not a valid Monero Mainnet address")
        # Prepare locally within monero-wallet-rpc but DO NOT relay yet. The user
        # reviews amount, fee, and destination before the separate relay call.
        result = self.call("transfer", {
            "destinations": [{"amount": amount_atomic, "address": destination}],
            "account_index": account_index,
            "priority": priority,
            "do_not_relay": True,
            "get_tx_metadata": True,
        }, request_id="prepare-transfer")
        fee = result.get("fee")
        tx_metadata = result.get("tx_metadata")
        tx_hash = result.get("tx_hash")
        if isinstance(fee, bool) or not isinstance(fee, int) or fee < 0:
            raise NetworkError("Monero wallet RPC did not return a valid fee")
        if (
            not isinstance(tx_metadata, str)
            or not tx_metadata
            or len(tx_metadata) > 2_000_000
            or any(ord(char) < 33 or ord(char) > 126 for char in tx_metadata)
        ):
            raise NetworkError("Monero wallet RPC did not return valid transaction metadata")
        if not isinstance(tx_hash, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", tx_hash):
            raise NetworkError("Monero wallet RPC did not return a valid transaction hash")
        if result.get("amount", amount_atomic) != amount_atomic:
            raise NetworkError("Monero RPC prepared a different amount than requested")
        return MoneroTransferPreview(destination, amount_atomic, fee, tx_hash, tx_metadata)

    def relay_transfer(self, preview: MoneroTransferPreview) -> str:
        result = self.call("relay_tx", {"hex": preview.tx_metadata}, request_id="relay-transfer")
        tx_hash = result.get("tx_hash")
        if not isinstance(tx_hash, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", tx_hash):
            raise NetworkError("Monero wallet RPC did not confirm a valid transaction hash")
        if tx_hash.lower() != preview.tx_hash.lower():
            raise NetworkError("Relayed Monero transaction hash did not match the preview")
        return tx_hash.lower()


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None
