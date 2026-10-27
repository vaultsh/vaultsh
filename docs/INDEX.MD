# Documentation index — Vaultsh 1.0.0-beta.1

**Languages:** [English](INDEX.md) · [Polski](pl/INDEX.md) · [Русский](ru/INDEX.md) · [English README](../README.md) · [Polski README](../README.pl.md) · [Русский README](../README.ru.md)

Vaultsh is a beta, local-first, self-custody cryptocurrency wallet. It has not received an independent security audit. Do not use significant funds; the Bitcoin change-address limitation below makes BTC sends especially unsuitable for real funds.

## What is currently implemented

- Encrypted local vault with versioned wallet records and password-derived AES-GCM encryption.
- BIP-39 phrase-based wallet creation/recovery for Bitcoin, Ethereum Mainnet and Solana Mainnet (English 12/24 word phrases; empty BIP-39 passphrase).
- Public-address QR display and PNG export for recognized BTC/EVM/XMR/SOL address shapes. QR checks are format guards, not a complete checksum/ownership proof.
- Read-only balance/history queries for one Bitcoin address and native balance queries for five EVM mainnets.
- Locally signed native transactions: BTC P2WPKH, ETH legacy EIP-155 on Ethereum Mainnet, SOL on Solana Mainnet. Sends require a user-selected endpoint, TOML network permission, `--allow-network`, a review, and an exact typed confirmation.
- Monero wallet create/open/close/address/balance/send through the official local `monero-wallet-rpc`. Monero wallet files/seed live outside the Vaultsh vault.
- Textual terminal UI, with a Rich dashboard fallback for non-interactive output.

## Key limitations

- **Bitcoin sends only scan confirmed UTXOs for the first receive address** and use BIP-84 change path `/1/0`, which Vaultsh does not currently scan. Change remains recoverable from the seed in a compatible wallet but may be invisible/unspendable inside Vaultsh. Do not use the BTC send command with real funds.
- ETH send supports native ETH on chain ID 1 only, with legacy `gasPrice` transactions; no ERC-20, EIP-1559, contract calls or receipt/finality polling.
- SOL send supports native SOL only; no SPL tokens, full wallet discovery, history, or finality polling.
- Other EVM profiles (Polygon, Arbitrum, Optimism and Base) are read-only.
- Monero needs a separately installed and correctly configured `monero-wallet-rpc` plus a synced/verified daemon. RPC must remain loopback-only.
- No implemented Tor transport, hardware wallet, multisig, independent audit or real-node integration validation in this release.

## Documents

- [Architecture](ARCHITECTURE.md)
- [CLI reference](CLI_REFERENCE.md)
- [Configuration](CONFIGURATION.md)
- [Network adapters](NETWORK_ADAPTERS.md)
- [Vault format](VAULT_FORMAT.md)
- [Security model](SECURITY_MODEL.md)
- [Test results](TEST_RESULTS.md)
- [Development guide](DEVELOPMENT.md)
- [Textual UI](INTERFACE.md)
- [Roadmap](ROADMAP.md)
- [Security policy](../SECURITY.md)
- [Contributing](../CONTRIBUTING.md)

## Test status

Latest local run: **194 passed, 7 skipped; 53% measured line coverage** on Python 3.13.5/Linux. Skips are dependency-gated. No live public RPC/Esplora requests and no real transaction broadcasts were performed in the build environment. See [test results](TEST_RESULTS.md).
