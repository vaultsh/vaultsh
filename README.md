<div align="center">

# Vaultsh

### A privacy-conscious, self-custodial cryptocurrency CLI foundation

**Local-first. Private by default. Explicit network access.**

[![License: GPL-3.0-only](https://img.shields.io/badge/License-GPL--3.0--only-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Pre--alpha-orange.svg)](#project-status)

</div>

**🌐 Documentation / Dokumentacja / Документация:** [English](README.md) · [Polski](README.pl.md) · [Русский](README.ru.md)

---

## Project status

**Vaultsh 0.6.0 is pre-alpha, has not been independently audited, and must not be used to store or transact real funds.** It combines encrypted local vault files and backups with offline Bitcoin Mainnet wallet creation/recovery, plus explicitly authorized read-only network queries for Bitcoin and five EVM mainnets: Ethereum, Polygon PoS, Arbitrum One, Optimism, and Base.

This is not yet a complete multi-chain wallet. Bitcoin wallet creation and recovery are implemented for a limited BIP-39/BIP-84 flow. EVM support is **read-only native-asset balance lookup** across five explicitly named mainnets; it does not include EVM wallet key derivation/storage, ERC-20 tokens, transaction history, transaction construction, signing, or broadcasting. Monero is not implemented.

Vaultsh is written in Python and aims to support Windows 10/11, Linux, and Android through Termux. Each platform still requires dedicated compatibility testing; a listed platform is not a claim of production readiness.

## What's new in 0.6.0

- Added a bounded, newest-first **Bitcoin address transaction history** query via a user-selected Esplora-compatible endpoint.
- Added native balance lookup via JSON-RPC for five EVM mainnets: Ethereum (`chainId=1`, ETH), Polygon PoS (`137`, POL), Arbitrum One (`42161`, ETH), Optimism (`10`, ETH), and Base (`8453`, ETH). Each endpoint must return the selected profile's `eth_chainId` before `eth_getBalance` is requested.
- Added EVM address syntax validation and EIP-55 checksum validation for mixed-case addresses.
- Kept network access disabled by default. Every read-only query requires both `network_requests_enabled = true` in the chosen TOML file and the CLI flag `--allow-network`.
- Kept endpoint choice explicit. Remote endpoints must use HTTPS; HTTP is allowed only for localhost/loopback. Redirects and ambient proxy environment variables are disabled for these clients.
- Added offline tests for EVM JSON-RPC responses, profile-specific chain-ID enforcement, address/endpoint validation, and Bitcoin transaction-history parsing/CLI behavior.
- Updated the command reference, architecture, security model, roadmap, changelog, and configuration documentation.

## Current feature matrix

| Capability | Bitcoin Mainnet | EVM mainnets (5 profiles) | Monero |
|---|---|---|---|
| Offline wallet creation/recovery | Limited BIP-39/BIP-84 | Not implemented | Not implemented |
| Public-address validation | Supported Mainnet formats using `embit` | 20-byte `0x` hex; mixed-case EIP-55 checksum checked | Not implemented |
| Read-only balance lookup | Yes, address-scoped via Esplora | Yes, native asset via JSON-RPC for Ethereum, Polygon, Arbitrum, Optimism, and Base | Not implemented |
| Address transaction history | First-page query, max 25 rows | Not implemented | Not implemented |
| Wallet-wide discovery/aggregation | Not implemented | Not implemented | Not implemented |
| Transaction preview/signing/broadcast | Not implemented | Not implemented | Not implemented |
| Token balances | Not applicable to this adapter | ERC-20 not implemented | Not implemented |
| Tor transport | Not implemented | Not implemented | Not implemented |

A feature marked as supported is not independently audited. Read-only balances/history are provider-supplied data, not cryptographic proofs of ownership or complete wallet state.

### Local test result for 0.6.0

The latest local run on 2026-10-27 completed with **144 passed, 4 skipped, and 82% measured line coverage** (`pytest --cov=vaultsh --cov-report=term-missing -q`, Python 3.13.5). The four skips were dependency-gated tests because `embit` and `eth-utils` were unavailable in that environment. Five UI-language regression tests were added; the detailed report covers the current source tree. No live network request was made, hosted Windows/Linux CI was not observed, and these numbers are not a security certification. See [the complete test report](docs/TEST_RESULTS.md).

## Documentation

- [English documentation index](docs/INDEX.md)
- [Polish documentation index](docs/pl/INDEX.md)
- [Russian documentation index](docs/ru/INDEX.md)
- [Architecture](docs/ARCHITECTURE.md)
- [CLI reference](docs/CLI_REFERENCE.md)
- [Configuration reference](docs/CONFIGURATION.md)
- [Encrypted vault format](docs/VAULT_FORMAT.md)
- [Security model](docs/SECURITY_MODEL.md)
- [Network adapters](docs/NETWORK_ADAPTERS.md)
- [Test results and known gaps](docs/TEST_RESULTS.md)
- [Development and testing](docs/DEVELOPMENT.md)
- [Roadmap](docs/ROADMAP.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Changelog](CHANGELOG.md)

## Interface languages

The start dashboard and top-level informational screens support English, Polish, and Russian. Pass `--lang` before the command; for example `vaultsh --lang pl` or `vaultsh --lang ru about`. Detailed command help, operation prompts, and some low-level error messages remain English in this release. The links above switch the full README and documentation set.

## Installation

Use Python 3.12 or newer. From the repository root:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux / macOS / Termux: source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

The `eth-utils` and `eth-hash[pycryptodome]` dependencies are used for mixed-case EIP-55 checksum validation. `embit` provides Bitcoin BIP-39/BIP-32/BIP-84 primitives. Dependency installation should happen in a trusted environment and dependency versions should be reviewed before production use.

Check the installed version and commands:

```bash
vaultsh version
vaultsh --help
vaultsh networks
vaultsh privacy
```

## Quick start: encrypted vault and Bitcoin wallet

Create a local encrypted vault. The password is entered in a hidden prompt and must contain at least 12 characters:

```bash
vaultsh vault init ./main.vault --label "Main Vault"
```

Create an offline Bitcoin Mainnet wallet in that vault:

```bash
vaultsh wallet create --vault ./main.vault --label "Bitcoin Main"
```

The command displays a recovery phrase once for offline backup. The phrase is also kept inside the authenticated encrypted vault payload. Store the phrase offline. Anyone with the phrase can control the associated wallet.

List public wallet metadata without displaying recovery phrases:

```bash
vaultsh wallet list --vault ./main.vault
```

Create a byte-for-byte encrypted backup:

```bash
vaultsh vault backup ./main.vault ./main.vault.backup
vaultsh vault check ./main.vault.backup
```

The `vault check` command prompts for the password and validates the encrypted payload.

## Read-only network queries

Network use is opt-in twice. Generate a non-secret configuration template:

```bash
vaultsh config-init ./vaultsh.toml
```

Edit the `[app]` table and change `network_requests_enabled` to `true` only when you intend to make network requests. Keep `tor_enabled = false`: this release does not route traffic through Tor, and query commands refuse to connect if it is set to `true`.

### Bitcoin balance

```bash
vaultsh bitcoin balance ADDRESS \
  --endpoint https://YOUR-ESPLORA-ENDPOINT/api \
  --config ./vaultsh.toml \
  --allow-network
```

### Bitcoin address transaction history

```bash
vaultsh bitcoin history ADDRESS \
  --endpoint https://YOUR-ESPLORA-ENDPOINT/api \
  --config ./vaultsh.toml \
  --allow-network \
  --limit 10
```

The history command returns at most 25 records from the first response page for a **single address**. It does not discover the wallet's other addresses or claim to be a complete wallet history.

### EVM native-asset balance

```bash
vaultsh ethereum balance 0xYOUR_40_HEX_CHARACTER_ADDRESS \
  --endpoint https://YOUR-ETHEREUM-JSON-RPC-ENDPOINT \
  --config ./vaultsh.toml \
  --allow-network

# Other supported EVM networks (change the endpoint to one for that chain)
vaultsh evm balance 0xYOUR_40_HEX_CHARACTER_ADDRESS --chain polygon \
  --endpoint https://YOUR-POLYGON-JSON-RPC-ENDPOINT \
  --config ./vaultsh.toml \
  --allow-network
```

The selected endpoint must match the selected chain profile. `vaultsh ethereum balance` targets Ethereum Mainnet only; `vaultsh evm balance --chain NETWORK` supports `ethereum`, `polygon`, `arbitrum`, `optimism`, and `base`. The command checks `eth_chainId` before requesting `eth_getBalance`, then formats the 18-decimal native asset using integer arithmetic. Polygon PoS is displayed as POL; the other profiles use ETH. It does not query ERC-20 tokens, create EVM wallets, derive EVM private keys, or retrieve EVM transaction history.

**Privacy warning:** the endpoint receives the queried public address and connection metadata, which can include the client's IP address and timing. Vaultsh does not choose a public provider, does not follow redirects, and does not use environment-configured proxies. Requests are direct; Tor transport is not implemented. Prefer a trusted self-hosted node or endpoint if you understand how to operate it securely.

## Security and limitations

- Vaultsh is pre-alpha and unaudited. Do not use it to store or transact real funds.
- The encrypted vault uses password-based Scrypt key derivation and AES-256-GCM authenticated encryption. This implementation and its file format need independent review.
- Bitcoin wallet derivation is limited to the first BIP-84 Mainnet receiving address at `m/84'/0'/0'/0/0`. The code does not scan address gaps or aggregate all wallet balances.
- Bitcoin recovery supports English BIP-39 12- and 24-word phrases with an empty BIP-39 passphrase only.
- EVM support is limited to read-only native-asset balance queries for Ethereum, Polygon PoS, Arbitrum One, Optimism, and Base. The application does not hold or derive EVM private keys.
- EVM transaction history, ERC-20 token balances, Monero, Tor transport, transaction previews, signing, and broadcasting are not implemented.
- A growing test suite is not a security certification. See [Test results](docs/TEST_RESULTS.md) for environment limitations and skipped tests.

See [SECURITY.md](SECURITY.md) before reporting a vulnerability. Never include recovery phrases, passwords, vault files, or private keys in issue reports.

## License

Vaultsh is distributed under **GPL-3.0-only**. See [LICENSE](LICENSE).
