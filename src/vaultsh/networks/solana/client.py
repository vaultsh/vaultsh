"""Solana Mainnet RPC and locally signed native SOL transfers."""
from __future__ import annotations

import base64
import ipaddress
import json
import re
from dataclasses import dataclass, field
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from vaultsh.networks.base import NetworkError
from vaultsh.networks.wallet_derivation import derive_solana_keypair

MAINNET_GENESIS_HASH = "5eykt4UsFv8P8NJdTREpY1vzqKqZKvdpKuc147dw2N9d"
MAX_RESPONSE_BYTES = 1_000_000
MAX_LAMPORTS = (1 << 64) - 1
_SIGNATURE_RE = re.compile(r"[1-9A-HJ-NP-Za-km-z]{64,90}\Z")


@dataclass(frozen=True, slots=True)
class SolanaTransferPreview:
    sender: str
    destination: str
    lamports: int
    fee_lamports: int
    blockhash: str
    signed_transaction_b64: str = field(repr=False)


def validate_solana_rpc_endpoint(endpoint: str) -> str:
    if not isinstance(endpoint, str) or not endpoint or len(endpoint) > 2048:
        raise NetworkError("An explicit Solana JSON-RPC endpoint is required")
    try:
        parsed = urlsplit(endpoint.strip())
        hostname = parsed.hostname
        _ = parsed.port
    except ValueError as exc:
        raise NetworkError("Solana endpoint URL is malformed") from exc
    if parsed.scheme not in {"https", "http"} or not parsed.netloc or not hostname:
        raise NetworkError("Solana endpoint must be HTTPS or localhost HTTP")
    if parsed.username is not None or parsed.password is not None or parsed.query or parsed.fragment:
        raise NetworkError("Solana endpoint must not contain URL credentials, query or fragment")
    if any(ord(char) < 32 or ord(char) == 127 for char in endpoint):
        raise NetworkError("Solana endpoint contains control characters")
    loopback = hostname.casefold() == "localhost"
    try:
        loopback = loopback or ipaddress.ip_address(hostname).is_loopback
    except ValueError:
        pass
    if parsed.scheme == "http" and not loopback:
        raise NetworkError("Plain HTTP is allowed only for a local Solana RPC endpoint")
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", ""))


def format_sol(lamports: int) -> str:
    """Format lamports as SOL using integer arithmetic only."""
    if isinstance(lamports, bool) or not isinstance(lamports, int) or not 0 <= lamports <= MAX_LAMPORTS:
        raise NetworkError("Invalid lamport amount")
    whole, fraction = divmod(lamports, 1_000_000_000)
    return f"{whole}.{fraction:09d}".rstrip("0").rstrip(".") if fraction else str(whole)


def sol_to_lamports(amount: str) -> int:
    from decimal import Decimal, InvalidOperation

    if not isinstance(amount, str) or not amount.strip() or len(amount) > 80:
        raise NetworkError("SOL amount must be a positive decimal string")
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", amount.strip()):
        raise NetworkError("SOL amount must use plain decimal notation")
    try:
        value = Decimal(amount.strip())
    except InvalidOperation as exc:
        raise NetworkError("SOL amount is invalid") from exc
    if not value.is_finite() or value <= 0 or value.as_tuple().exponent < -9:
        raise NetworkError("SOL amount must be positive and have at most 9 decimal places")
    units = value * 1_000_000_000
    if units != units.to_integral_value() or int(units) > MAX_LAMPORTS:
        raise NetworkError("SOL amount is outside the supported range")
    return int(units)


class SolanaRpcClient:
    def __init__(self, endpoint: str, *, timeout_seconds: float = 15.0, opener: Any | None = None):
        self.endpoint = validate_solana_rpc_endpoint(endpoint)
        if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, (int, float)) or not 0.1 <= timeout_seconds <= 300:
            raise NetworkError("Timeout must be between 0.1 and 300 seconds")
        self.timeout_seconds = float(timeout_seconds)
        self._opener = opener or build_opener(ProxyHandler({}), _NoRedirectHandler())

    def call(self, method: str, params: list[Any] | None = None, request_id: int = 1) -> Any:
        body = json.dumps({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params or []}, separators=(",", ":")).encode()
        req = Request(self.endpoint, data=body, method="POST", headers={"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "Vaultsh/1.0.0b1"})
        try:
            with self._opener.open(req, timeout=self.timeout_seconds) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
        except HTTPError as exc:
            if 300 <= exc.code < 400:
                raise NetworkError("Solana RPC redirects are blocked") from exc
            raise NetworkError(f"Solana RPC returned HTTP status {exc.code}") from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise NetworkError("Solana RPC request failed; check endpoint and connection") from exc
        if len(raw) > MAX_RESPONSE_BYTES:
            raise NetworkError("Solana RPC response exceeded the configured size limit")
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise NetworkError("Solana RPC returned invalid JSON") from exc
        if not isinstance(payload, dict) or payload.get("jsonrpc") != "2.0" or payload.get("id") != request_id:
            raise NetworkError("Solana RPC response did not match the request")
        if payload.get("error") is not None or "result" not in payload:
            raise NetworkError(f"Solana RPC method {method} failed")
        return payload["result"]

    def ensure_mainnet(self) -> None:
        genesis = self.call("getGenesisHash", request_id=10)
        if genesis != MAINNET_GENESIS_HASH:
            raise NetworkError("Selected endpoint is not Solana Mainnet Beta")

    @staticmethod
    def _validate_address(address: str) -> str:
        # A Solana public key is exactly 32 bytes encoded using Bitcoin's
        # base58 alphabet. Keep this check dependency-free for read-only CLI use.
        alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        if not isinstance(address, str) or not 32 <= len(address) <= 44 or any(ch not in alphabet for ch in address):
            raise NetworkError("Invalid Solana public address")
        number = 0
        for char in address:
            number = number * 58 + alphabet.index(char)
        raw = number.to_bytes((number.bit_length() + 7) // 8, "big") if number else b""
        leading_zeroes = len(address) - len(address.lstrip("1"))
        decoded = b"\x00" * leading_zeroes + raw
        if len(decoded) != 32:
            raise NetworkError("Invalid Solana public address length")
        return address

    def get_balance(self, address: str) -> int:
        address = self._validate_address(address)
        self.ensure_mainnet()
        result = self.call("getBalance", [address, {"commitment": "confirmed"}], request_id=11)
        value = result.get("value") if isinstance(result, dict) else None
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= MAX_LAMPORTS:
            raise NetworkError("Solana RPC returned an invalid balance")
        return value

    def prepare_transfer(self, *, mnemonic: str, expected_sender: str, destination: str, amount: str, max_fee_sol: str = "0.01") -> SolanaTransferPreview:
        try:
            from solders.hash import Hash
            from solders.pubkey import Pubkey
            from solders.message import Message
            from solders.system_program import TransferParams, transfer
            from solders.transaction import Transaction
        except ImportError as exc:
            raise NetworkError("Solana transfers require solders; install project dependencies") from exc
        sender_key = derive_solana_keypair(mnemonic)
        sender = str(sender_key.pubkey())
        if sender != expected_sender:
            raise NetworkError("Derived signing key does not match the selected Solana wallet")
        try:
            destination = str(Pubkey.from_string(destination))
            to_pubkey = Pubkey.from_string(destination)
        except Exception as exc:
            raise NetworkError("Invalid Solana destination address") from exc
        lamports = sol_to_lamports(amount)
        max_fee = sol_to_lamports(max_fee_sol)
        self.ensure_mainnet()
        balance_result = self.call("getBalance", [sender, {"commitment": "confirmed"}], request_id=12)
        balance = balance_result.get("value") if isinstance(balance_result, dict) else None
        latest = self.call("getLatestBlockhash", [{"commitment": "confirmed"}], request_id=13)
        try:
            blockhash_text = latest["value"]["blockhash"]
            blockhash = Hash.from_string(blockhash_text)
            instruction = transfer(TransferParams(from_pubkey=sender_key.pubkey(), to_pubkey=to_pubkey, lamports=lamports))
            message = Message.new_with_blockhash([instruction], sender_key.pubkey(), blockhash)
            message_b64 = base64.b64encode(bytes(message)).decode("ascii")
            fee_result = self.call("getFeeForMessage", [message_b64, {"commitment": "confirmed"}], request_id=14)
            fee = fee_result.get("value") if isinstance(fee_result, dict) else None
        except Exception as exc:
            if isinstance(exc, NetworkError):
                raise
            raise NetworkError("Could not prepare the Solana transfer message") from exc
        if isinstance(balance, bool) or not isinstance(balance, int) or balance < 0:
            raise NetworkError("Solana RPC returned an invalid sender balance")
        if isinstance(fee, bool) or not isinstance(fee, int) or fee < 0:
            raise NetworkError("Solana RPC could not estimate the transfer fee")
        if fee > max_fee:
            raise NetworkError("Estimated SOL network fee exceeds the configured maximum")
        if lamports + fee > balance:
            raise NetworkError("Insufficient SOL for amount plus network fee")
        try:
            transaction = Transaction.new_unsigned(message)
            transaction.sign([sender_key], blockhash)
            signed_b64 = base64.b64encode(bytes(transaction)).decode("ascii")
        except Exception as exc:
            raise NetworkError("Could not sign the Solana transfer") from exc
        return SolanaTransferPreview(sender, destination, lamports, fee, blockhash_text, signed_b64)

    def broadcast_transfer(self, preview: SolanaTransferPreview) -> str:
        result = self.call("sendTransaction", [preview.signed_transaction_b64, {"encoding": "base64", "skipPreflight": False, "preflightCommitment": "confirmed", "maxRetries": 3}], request_id=15)
        if not isinstance(result, str) or not _SIGNATURE_RE.fullmatch(result):
            raise NetworkError("Solana RPC returned an invalid transaction signature")
        return result


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None
