"""Chain-specific derivation for the supported single-account wallet profiles.

This module never writes key material to disk. Secrets are returned only to
callers that explicitly request derivation and should be discarded after use.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from vaultsh.networks.bitcoin.wallet import derive_first_receive_address, normalize_mnemonic

ETHEREUM_PATH = "m/44'/60'/0'/0/0"
SOLANA_PATH = "m/44'/501'/0'/0'"


@dataclass(frozen=True, slots=True)
class DerivedChainWallet:
    network: str
    address: str
    derivation_path: str
    mnemonic: str = field(repr=False)


class WalletDerivationError(ValueError):
    """Raised when a network-specific key/address derivation fails."""


def derive_chain_wallet(network: str, mnemonic: str) -> DerivedChainWallet:
    """Derive first receive address for Bitcoin, Ethereum or Solana Mainnet."""
    network = network.strip().lower() if isinstance(network, str) else ""
    normalized = normalize_mnemonic(mnemonic)
    if network == "bitcoin-mainnet":
        derived = derive_first_receive_address(normalized)
        return DerivedChainWallet(network, derived.address, derived.derivation_path, normalized)
    if network == "ethereum-mainnet":
        _bip32, bip39, _script = _load_embit()
        try:
            from eth_account import Account
        except ImportError as exc:
            raise WalletDerivationError("Ethereum support requires eth-account") from exc
        try:
            root = _bip32.HDKey.from_seed(bip39.mnemonic_to_seed(normalized))
            child = root.derive(ETHEREUM_PATH)
            secret = child.key.secret
            private_key = secret.to_bytes(32, "big") if isinstance(secret, int) else bytes(secret)
            if len(private_key) != 32:
                raise ValueError("Invalid derived private key length")
            address = Account.from_key(private_key).address
        except Exception as exc:
            raise WalletDerivationError("Could not derive the Ethereum wallet address") from exc
        return DerivedChainWallet(network, address, ETHEREUM_PATH, normalized)
    if network == "solana-mainnet":
        try:
            from bip_utils import Bip32Slip10Ed25519, Bip39SeedGenerator
            from solders.keypair import Keypair
        except ImportError as exc:
            raise WalletDerivationError("Solana support requires bip-utils and solders") from exc
        try:
            seed = Bip39SeedGenerator(normalized).Generate()
            node = Bip32Slip10Ed25519.FromSeed(seed).DerivePath(SOLANA_PATH)
            private_key = node.PrivateKey().Raw().ToBytes()
            keypair = Keypair.from_seed(private_key)
            address = str(keypair.pubkey())
        except Exception as exc:
            raise WalletDerivationError("Could not derive the Solana wallet address") from exc
        return DerivedChainWallet(network, address, SOLANA_PATH, normalized)
    raise WalletDerivationError("Supported wallet profiles: bitcoin-mainnet, ethereum-mainnet, solana-mainnet")


def derive_evm_private_key(mnemonic: str, network: str = "ethereum-mainnet") -> bytes:
    """Derive a secp256k1 private key using the Ethereum BIP-44 path."""
    if network != "ethereum-mainnet":
        raise WalletDerivationError("Only Ethereum Mainnet wallet records are supported here")
    normalized = normalize_mnemonic(mnemonic)
    bip32, bip39, _script = _load_embit()
    try:
        key = bip32.HDKey.from_seed(bip39.mnemonic_to_seed(normalized)).derive(ETHEREUM_PATH).key
        secret = key.secret
        private_key = secret.to_bytes(32, "big") if isinstance(secret, int) else bytes(secret)
        if len(private_key) != 32 or not any(private_key):
            raise ValueError("Invalid private key")
        return private_key
    except Exception as exc:
        raise WalletDerivationError("Could not derive the Ethereum private key") from exc


def derive_solana_keypair(mnemonic: str):
    """Derive a Solana Mainnet keypair using m/44'/501'/0'/0'."""
    normalized = normalize_mnemonic(mnemonic)
    try:
        from bip_utils import Bip32Slip10Ed25519, Bip39SeedGenerator
        from solders.keypair import Keypair
        seed = Bip39SeedGenerator(normalized).Generate()
        private_key = Bip32Slip10Ed25519.FromSeed(seed).DerivePath(SOLANA_PATH).PrivateKey().Raw().ToBytes()
        return Keypair.from_seed(private_key)
    except ImportError as exc:
        raise WalletDerivationError("Solana support requires bip-utils and solders") from exc
    except Exception as exc:
        raise WalletDerivationError("Could not derive the Solana private key") from exc


def _load_embit():
    try:
        from embit import bip32, bip39, script
    except ImportError as exc:
        raise WalletDerivationError("Wallet derivation requires embit") from exc
    return bip32, bip39, script
