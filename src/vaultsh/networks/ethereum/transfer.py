"""Locally signed native-asset EVM transfers with an explicit preview step."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any

from vaultsh.networks.base import NetworkError
from vaultsh.networks.ethereum.client import (
    EVM_NETWORKS,
    EvmJsonRpcClient,
    _QUANTITY_PATTERN,
    validate_ethereum_address,
)
from vaultsh.networks.wallet_derivation import derive_evm_private_key

_TX_HASH = re.compile(r"0x[0-9a-fA-F]{64}\Z")


@dataclass(frozen=True, slots=True)
class EvmTransferPreview:
    network_name: str
    asset_symbol: str
    sender: str
    destination: str
    amount_base_units: int
    gas_limit: int
    gas_price_wei: int
    max_fee_wei: int
    nonce: int
    chain_id: int
    raw_signed_transaction: str = field(repr=False)


def parse_decimal_units(value: str, *, decimals: int, asset_symbol: str) -> int:
    """Parse a positive decimal amount into integer base units without float math."""
    if not isinstance(value, str) or len(value) > 80 or not value.strip():
        raise NetworkError(f"Amount for {asset_symbol} must be a positive decimal string")
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", value.strip()):
        raise NetworkError(f"Amount for {asset_symbol} must use plain decimal notation")
    try:
        amount = Decimal(value.strip())
    except InvalidOperation as exc:
        raise NetworkError(f"Amount for {asset_symbol} is not a valid decimal") from exc
    if not amount.is_finite() or amount <= 0:
        raise NetworkError(f"Amount for {asset_symbol} must be positive and finite")
    exponent = amount.as_tuple().exponent
    if exponent < -decimals:
        raise NetworkError(f"Amount for {asset_symbol} has more than {decimals} decimal places")
    units = amount * (10**decimals)
    if units != units.to_integral_value():
        raise NetworkError(f"Amount for {asset_symbol} cannot be represented exactly")
    result = int(units)
    if result <= 0 or result >= 2**256:
        raise NetworkError(f"Amount for {asset_symbol} is outside the supported range")
    return result


def _quantity(value: Any, field: str) -> int:
    if not isinstance(value, str) or not _QUANTITY_PATTERN.fullmatch(value):
        raise NetworkError(f"RPC returned an invalid {field} quantity")
    return int(value, 16)


def prepare_evm_transfer(
    *,
    endpoint: str,
    network: str,
    mnemonic: str,
    expected_sender: str,
    destination: str,
    amount: str,
    timeout_seconds: float = 15.0,
    max_fee_native: str = "0.1",
    client: EvmJsonRpcClient | None = None,
) -> EvmTransferPreview:
    """Query fee/nonce/balance then locally sign an ETH/native-asset transfer.

    The returned signed transaction is not broadcast. The caller must show the
    preview and obtain explicit user confirmation before calling
    :func:`broadcast_evm_transfer`.
    """
    try:
        profile = EVM_NETWORKS[network.strip().lower()]
    except (KeyError, AttributeError) as exc:
        raise NetworkError("Unsupported EVM network profile") from exc
    checked_destination = validate_ethereum_address(destination)
    rpc = client or EvmJsonRpcClient(
        endpoint,
        timeout_seconds=timeout_seconds,
        expected_chain_id=profile.chain_id,
        network_name=profile.name,
        asset_symbol=profile.asset_symbol,
    )
    try:
        from eth_account import Account
    except ImportError as exc:
        raise NetworkError("EVM signing requires eth-account; install project dependencies") from exc
    private_key = derive_evm_private_key(mnemonic)
    account = Account.from_key(private_key)
    sender = account.address
    validate_ethereum_address(expected_sender)
    if sender.lower() != expected_sender.lower():
        raise NetworkError("Derived signing key does not match the selected wallet address")

    chain_id = _quantity(rpc._rpc_call("eth_chainId", [], 101), "chain ID")
    if chain_id != profile.chain_id:
        raise NetworkError(
            f"Endpoint is not {profile.name}: expected chain ID {profile.chain_id}, received {chain_id}"
        )
    amount_units = parse_decimal_units(amount, decimals=18, asset_symbol=profile.asset_symbol)
    max_fee = parse_decimal_units(max_fee_native, decimals=18, asset_symbol=profile.asset_symbol)
    nonce = _quantity(rpc._rpc_call("eth_getTransactionCount", [sender, "pending"], 102), "nonce")
    gas_price = _quantity(rpc._rpc_call("eth_gasPrice", [], 103), "gas price")
    balance = _quantity(rpc._rpc_call("eth_getBalance", [sender, "latest"], 104), "balance")
    gas_estimate = _quantity(
        rpc._rpc_call(
            "eth_estimateGas",
            [{"from": sender, "to": checked_destination, "value": hex(amount_units)}],
            105,
        ),
        "gas estimate",
    )
    if not 21_000 <= gas_estimate <= 100_000:
        raise NetworkError("Native transfer gas estimate is outside the supported safe range")
    gas_limit = max(21_000, (gas_estimate * 120 + 99) // 100)
    fee = gas_limit * gas_price
    if fee > max_fee:
        raise NetworkError(
            f"Estimated maximum network fee exceeds the configured cap ({max_fee_native} {profile.asset_symbol})"
        )
    if amount_units + fee > balance:
        raise NetworkError("Insufficient balance for amount plus maximum network fee")
    transaction = {
        "nonce": nonce,
        "gasPrice": gas_price,
        "gas": gas_limit,
        "to": checked_destination,
        "value": amount_units,
        "chainId": chain_id,
    }
    try:
        signed = account.sign_transaction(transaction)
        raw_bytes = getattr(signed, "raw_transaction", None)
        if raw_bytes is None:  # compatibility with older eth-account API releases
            raw_bytes = signed.rawTransaction
        raw_hex = "0x" + bytes(raw_bytes).hex()
    except Exception as exc:
        raise NetworkError("Could not sign the prepared EVM transaction") from exc
    return EvmTransferPreview(
        network_name=profile.name,
        asset_symbol=profile.asset_symbol,
        sender=sender,
        destination=checked_destination,
        amount_base_units=amount_units,
        gas_limit=gas_limit,
        gas_price_wei=gas_price,
        max_fee_wei=fee,
        nonce=nonce,
        chain_id=chain_id,
        raw_signed_transaction=raw_hex,
    )


def broadcast_evm_transfer(
    preview: EvmTransferPreview, *, client: EvmJsonRpcClient
) -> str:
    """Broadcast a previously previewed and explicitly approved signed transaction."""
    result = client._rpc_call("eth_sendRawTransaction", [preview.raw_signed_transaction], 106)
    if not isinstance(result, str) or not _TX_HASH.fullmatch(result):
        raise NetworkError("EVM endpoint returned an invalid transaction hash")
    return result
