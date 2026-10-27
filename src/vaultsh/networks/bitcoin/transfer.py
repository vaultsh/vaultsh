"""Conservative Bitcoin Mainnet P2WPKH coin selection, signing and broadcast.

Only confirmed UTXOs at the wallet's first BIP-84 receive address are considered.
The implementation deliberately supports a single-input script type and performs
no change-address discovery beyond m/84'/0'/0'/1/0.
"""
from __future__ import annotations

import ipaddress
import json
import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, ROUND_CEILING
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from vaultsh.networks.base import NetworkError
from vaultsh.networks.bitcoin.client import MAX_MONEY_SATS, _validate_mainnet_address, validate_esplora_endpoint
from vaultsh.networks.bitcoin.wallet import normalize_mnemonic

_TXID_RE = re.compile(r"[0-9a-fA-F]{64}\Z")
DUST_SATS = 546
MAX_RESPONSE_BYTES = 2_000_000
HARDENED = 1 << 31


@dataclass(frozen=True, slots=True)
class BitcoinTransferPreview:
    sender: str
    destination: str
    amount_sats: int
    fee_sats: int
    input_count: int
    change_sats: int
    txid: str
    raw_transaction_hex: str = field(repr=False)


class BitcoinPaymentClient:
    def __init__(self, endpoint: str, *, timeout_seconds: float = 15.0, opener: Any | None = None):
        self.endpoint = validate_esplora_endpoint(endpoint)
        if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, (int, float)) or not 0.1 <= timeout_seconds <= 300:
            raise NetworkError("Timeout must be between 0.1 and 300 seconds")
        self.timeout_seconds = float(timeout_seconds)
        self._opener = opener or build_opener(ProxyHandler({}), _NoRedirectHandler())

    def _request(self, url: str, *, method: str = "GET", data: bytes | None = None, content_type: str | None = None) -> bytes:
        headers = {"Accept": "application/json", "User-Agent": "Vaultsh/1.0.0b1"}
        if content_type:
            headers["Content-Type"] = content_type
        req = Request(url, data=data, method=method, headers=headers)
        try:
            with self._opener.open(req, timeout=self.timeout_seconds) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
        except HTTPError as exc:
            if 300 <= exc.code < 400:
                raise NetworkError("Esplora redirects are blocked") from exc
            raise NetworkError(f"Esplora request failed with HTTP status {exc.code}") from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise NetworkError("Esplora request failed; check endpoint and connection") from exc
        if len(raw) > MAX_RESPONSE_BYTES:
            raise NetworkError("Esplora response exceeded the configured size limit")
        return raw

    def get_confirmed_utxos(self, address: str) -> list[dict[str, int | str]]:
        _validate_mainnet_address(address)
        path_address = quote(address, safe="")
        try:
            payload = json.loads(self._request(f"{self.endpoint}/address/{path_address}/utxo").decode())
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise NetworkError("Esplora returned invalid UTXO JSON") from exc
        if not isinstance(payload, list) or len(payload) > 10_000:
            raise NetworkError("Esplora returned an invalid UTXO list")
        outputs: list[dict[str, int | str]] = []
        seen: set[tuple[str, int]] = set()
        for row in payload:
            if not isinstance(row, dict):
                raise NetworkError("Esplora UTXO entry is invalid")
            txid, vout, value, status = row.get("txid"), row.get("vout"), row.get("value"), row.get("status")
            if not isinstance(txid, str) or not _TXID_RE.fullmatch(txid):
                raise NetworkError("Esplora returned an invalid UTXO txid")
            if isinstance(vout, bool) or not isinstance(vout, int) or not 0 <= vout <= 0xFFFFFFFF:
                raise NetworkError("Esplora returned an invalid UTXO output index")
            if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= MAX_MONEY_SATS:
                raise NetworkError("Esplora returned an invalid UTXO amount")
            if not isinstance(status, dict):
                raise NetworkError("Esplora UTXO status is missing")
            if status.get("confirmed") is True:
                key = (txid.lower(), vout)
                if key in seen:
                    raise NetworkError("Esplora returned duplicate UTXOs")
                seen.add(key)
                outputs.append({"txid": txid.lower(), "vout": vout, "value": value})
        return outputs

    def get_fee_rate(self) -> int:
        try:
            payload = json.loads(self._request(f"{self.endpoint}/fee-estimates").decode())
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise NetworkError("Esplora returned invalid fee estimate JSON") from exc
        if not isinstance(payload, dict):
            raise NetworkError("Esplora returned an invalid fee estimate response")
        candidates = (payload.get("2"), payload.get("3"), payload.get("6"), payload.get("1"))
        rate = None
        for candidate in candidates:
            if isinstance(candidate, (int, float)) and not isinstance(candidate, bool):
                rate = Decimal(str(candidate))
                break
        if rate is None or not rate.is_finite() or rate <= 0 or rate > 100:
            raise NetworkError("Fee estimate is invalid or exceeds the safety cap of 100 sat/vB")
        return int(rate.to_integral_value(rounding=ROUND_CEILING))

    def broadcast(self, transaction_hex: str) -> str:
        if not isinstance(transaction_hex, str) or not transaction_hex or len(transaction_hex) > 4_000_000 or len(transaction_hex) % 2:
            raise NetworkError("Signed transaction data is invalid")
        if not re.fullmatch(r"[0-9a-fA-F]+", transaction_hex):
            raise NetworkError("Signed transaction must be hexadecimal")
        try:
            result = self._request(f"{self.endpoint}/tx", method="POST", data=transaction_hex.encode("ascii"), content_type="text/plain").decode().strip()
        except UnicodeDecodeError as exc:
            raise NetworkError("Esplora returned an invalid transaction ID") from exc
        if not _TXID_RE.fullmatch(result):
            raise NetworkError("Esplora returned an invalid transaction ID")
        return result.lower()


def btc_to_sats(amount: str) -> int:
    if not isinstance(amount, str) or not amount.strip() or len(amount) > 80:
        raise NetworkError("BTC amount must be a positive decimal string")
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", amount.strip()):
        raise NetworkError("BTC amount must use plain decimal notation")
    try:
        value = Decimal(amount.strip())
    except InvalidOperation as exc:
        raise NetworkError("BTC amount is invalid") from exc
    if not value.is_finite() or value <= 0 or value.as_tuple().exponent < -8:
        raise NetworkError("BTC amount must be positive and have at most 8 decimal places")
    sats = value * 100_000_000
    if sats != sats.to_integral_value() or int(sats) > MAX_MONEY_SATS:
        raise NetworkError("BTC amount is outside the supported range")
    return int(sats)


def prepare_bitcoin_transfer(
    *, mnemonic: str, expected_sender: str, destination: str, amount: str,
    utxos: list[dict[str, int | str]], fee_rate_sat_vb: int, max_fee_sats: int = 100_000,
) -> BitcoinTransferPreview:
    """Build and locally sign a P2WPKH transaction without broadcasting it."""
    _validate_mainnet_address(expected_sender)
    _validate_mainnet_address(destination)
    normalized = normalize_mnemonic(mnemonic)
    if destination == expected_sender:
        raise NetworkError("Destination and sender addresses are identical")
    amount_sats = btc_to_sats(amount)
    if isinstance(fee_rate_sat_vb, bool) or not isinstance(fee_rate_sat_vb, int) or not 1 <= fee_rate_sat_vb <= 100:
        raise NetworkError("Fee rate must be an integer from 1 to 100 sat/vB")
    if isinstance(max_fee_sats, bool) or not isinstance(max_fee_sats, int) or not 1 <= max_fee_sats <= 10_000_000:
        raise NetworkError("Maximum fee must be from 1 to 10,000,000 satoshis")
    try:
        from embit import bip32, bip39
        from embit.finalizer import finalize_psbt
        from embit.psbt import DerivationPath, PSBT
        from embit.script import address_to_scriptpubkey, p2wpkh
        from embit.transaction import Transaction, TransactionInput, TransactionOutput
    except ImportError as exc:
        raise NetworkError("Bitcoin signing requires embit; install the project dependencies") from exc
    try:
        root = bip32.HDKey.from_seed(bip39.mnemonic_to_seed(normalized))
        receive_path = [84 + HARDENED, HARDENED, HARDENED, 0, 0]
        change_path = [84 + HARDENED, HARDENED, HARDENED, 1, 0]
        receive_key = root.derive("m/84'/0'/0'/0/0")
        change_key = root.derive("m/84'/0'/0'/1/0")
        if p2wpkh(receive_key.key).address() != expected_sender:
            raise NetworkError("Derived signing key does not match the selected Bitcoin wallet")
        destination_script = address_to_scriptpubkey(destination)
        change_script = p2wpkh(change_key.key)
    except NetworkError:
        raise
    except Exception as exc:
        raise NetworkError("Could not derive Bitcoin signing keys") from exc
    candidates = sorted(
        [row for row in utxos if isinstance(row, dict)],
        key=lambda row: int(row.get("value", 0)) if isinstance(row.get("value", 0), int) else 0,
        reverse=True,
    )
    validated: list[dict[str, int | str]] = []
    seen: set[tuple[str, int]] = set()
    for row in candidates:
        txid, vout, value = row.get("txid"), row.get("vout"), row.get("value")
        if not isinstance(txid, str) or not _TXID_RE.fullmatch(txid):
            raise NetworkError("UTXO txid is invalid")
        if isinstance(vout, bool) or not isinstance(vout, int) or not 0 <= vout <= 0xFFFFFFFF:
            raise NetworkError("UTXO output index is invalid")
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= MAX_MONEY_SATS:
            raise NetworkError("UTXO value is invalid")
        if (txid.lower(), vout) in seen:
            raise NetworkError("Duplicate UTXO detected")
        seen.add((txid.lower(), vout))
        validated.append({"txid": txid.lower(), "vout": vout, "value": value})

    selected: list[dict[str, int | str]] = []
    total = 0
    change = 0
    fee_sats = 0
    for utxo in validated:
        selected.append(utxo)
        total += int(utxo["value"])
        fee_with_change = fee_rate_sat_vb * (11 + len(selected) * 72 + 2 * 31)
        if total >= amount_sats + fee_with_change:
            change = total - amount_sats - fee_with_change
            fee_sats = fee_with_change
            break
    else:
        raise NetworkError("Insufficient confirmed Bitcoin funds for amount plus fee")
    outputs = [TransactionOutput(amount_sats, destination_script)]
    if change >= DUST_SATS:
        outputs.append(TransactionOutput(change, change_script))
    else:
        # Donate sub-dust residue to fees rather than creating an uneconomic output.
        fee_sats += change
        change = 0
    if fee_sats > max_fee_sats:
        raise NetworkError("Estimated Bitcoin network fee exceeds configured maximum")
    try:
        tx_inputs = [TransactionInput(bytes.fromhex(str(row["txid"])), int(row["vout"])) for row in selected]
        tx = Transaction(version=2, vin=tx_inputs, vout=outputs, locktime=0)
        psbt = PSBT(tx)
        for index, utxo in enumerate(selected):
            scope = psbt.inputs[index]
            scope.witness_utxo = TransactionOutput(int(utxo["value"]), address_to_scriptpubkey(expected_sender))
            scope.sighash_type = 1
            child_pubkey = root.derive("m/84'/0'/0'/0/0").key.get_public_key()
            scope.bip32_derivations[child_pubkey] = DerivationPath(root.my_fingerprint, receive_path)
        psbt.sign_with(root)
        finalized = finalize_psbt(psbt)
        raw_tx = finalized.serialize().hex()
        txid = finalized.txid().hex()
        actual_fee = total - sum(int(item.value) for item in finalized.vout)
        if actual_fee < 0 or actual_fee > max_fee_sats:
            raise NetworkError("Finalized Bitcoin transaction fee is outside the configured range")
        return BitcoinTransferPreview(expected_sender, destination, amount_sats, actual_fee, len(selected), change, txid, raw_tx)
    except NetworkError:
        raise
    except Exception as exc:
        raise NetworkError("Could not build and sign the Bitcoin transaction") from exc


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None
