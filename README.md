<div align="center">

# Vaultsh

### A privacy-focused, self-custodial cryptocurrency wallet foundation for the terminal

**Private by default. Local-first. Built for the command line.**

[![License: GPL-3.0-only](https://img.shields.io/badge/License-GPL--3.0--only-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Pre--alpha-orange.svg)](#project-status)

</div>

---

## Project status

**Vaultsh 0.4.5 is pre-alpha, has not been independently audited, and must not be used to store or transact real funds.** It provides local encrypted vaults, offline Bitcoin Mainnet wallet creation/recovery, first-address BIP-84 derivation, and an explicitly authorized read-only balance lookup against a user-selected Esplora-compatible API. It does not scan the full wallet's address range, discover used addresses, build or sign transactions, or broadcast payments.

Vaultsh is written in Python and is intended to grow into a privacy-conscious multi-chain CLI for Windows 10/11, Linux, and Android through Termux. Compatibility with each target must be tested; these platforms are goals, not a claim of validated production support.

## Documentation

- [Full documentation index](docs/INDEX.md)
- [Architecture and module boundaries](docs/ARCHITECTURE.md)
- [CLI reference](docs/CLI_REFERENCE.md)
- [Configuration reference](docs/CONFIGURATION.md)
- [Encrypted vault format](docs/VAULT_FORMAT.md)
- [Security model and limitations](docs/SECURITY_MODEL.md)
- [Development and testing](docs/DEVELOPMENT.md)
- [Roadmap](docs/ROADMAP.md)
- [Contributing and commit-message style](CONTRIBUTING.md)
- [Security vulnerability reporting](SECURITY.md)
- [Version history](CHANGELOG.md)

## Features in 0.4.5

- Rich terminal UI and Typer-based CLI.
- Password-protected local vault files using Scrypt key derivation and AES-256-GCM authenticated encryption.
- Bitcoin Mainnet English BIP-39 phrase generation from 128 bits of operating-system entropy (12 words generated).
- Recovery from valid English BIP-39 12- or 24-word phrases, using an empty BIP-39 passphrase only.
- First BIP-84 Native SegWit receiving-address derivation at `m/84'/0'/0'/0/0`, delegated to `embit`.
- Wallet metadata and recovery phrases stored inside the authenticated encrypted vault payload; normal listing omits phrases.
- Explicit confirmation and vault-password prompt before revealing a stored recovery phrase.
- Encrypted byte-for-byte backup and restore helpers, plus versioned vault schema support.
- Non-secret TOML configuration validation with telemetry and network access disabled by default.
- **Read-only Bitcoin Mainnet address-balance query** using a user-supplied Esplora-compatible endpoint. Both `network_requests_enabled = true` in the supplied TOML config and the CLI flag `--allow-network` are required.
- Strict endpoint checks: HTTPS for remote endpoints, HTTP only for localhost/loopback, no URL credentials/query/fragments, no automatic redirects, no ambient proxy environment variables, bounded responses, and request timeouts.
- If `tor_enabled = true`, the balance command refuses to connect rather than silently making a direct connection; Tor transport is not implemented.

## Not implemented

- Full wallet address discovery, gap-limit scanning, balance aggregation across all derived addresses, or complete transaction history.
- Fee estimation, transaction construction, PSBT creation/signing, or broadcast.
- Bitcoin Core RPC integration and local node-management features.
- Ethereum/EVM and Monero wallet support.
- Live Tor transport. The Tor module does not start Tor or route application traffic.
- BIP-39 languages other than English or non-empty optional BIP-39 passphrases.
- Independent audit, production hardening, or a guarantee of anonymity.

## Requirements

- Python 3.12 or newer.
- `pip` and network access during installation to obtain dependencies.
- Runtime dependencies declared in `pyproject.toml`: Typer, Rich, `cryptography`, and `embit`.
- Development extras: pytest, pytest-cov, Ruff, and mypy.

## Installation

Run commands from the extracted/cloned repository root (`vaultsh/`).

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### Android / Termux

The same virtual-environment commands may work where supported, but Termux is not currently covered by an automated compatibility matrix. Test locally before relying on it.

## Quick start

### 1. Create an encrypted vault

```bash
vaultsh vault init ./main.vault --label "Main vault"
```

Vaultsh asks for a password twice without echoing it. New vault passwords must contain at least 12 characters. Length alone does not guarantee strength; use a unique, high-entropy password.

### 2. Create a Bitcoin wallet

```bash
vaultsh wallet create --vault ./main.vault --label "Bitcoin Main"
```

The command generates a 12-word English BIP-39 phrase offline, derives the first BIP-84 Mainnet Native SegWit address, stores the phrase inside the encrypted vault, and displays the phrase once. Record it offline and never share it. **Do not send funds to this pre-alpha software.**

### 3. List wallet metadata

```bash
vaultsh wallet list --vault ./main.vault
```

This lists public wallet metadata and receive addresses. It does not scan other derivation paths or aggregate balances across the wallet.

### 4. Recover a wallet

```bash
vaultsh wallet recover --vault ./main.vault --label "Recovered Bitcoin wallet"
```

Enter the phrase at the hidden prompt. Only valid English BIP-39 12- or 24-word phrases are accepted. The optional BIP-39 passphrase must be empty; a wallet originally created with a non-empty passphrase derives different keys and addresses.

### 5. Reveal a stored phrase

```bash
vaultsh wallet recovery-phrase <WALLET_ID> --vault ./main.vault
```

The command asks for explicit confirmation and then the vault password. Use this only in a private environment. A terminal, operating system, screen recorder, clipboard manager, or malicious process may capture secrets.

### 6. Check or back up a vault

```bash
vaultsh vault check ./main.vault
vaultsh vault backup ./main.vault ./main.vault.backup
vaultsh vault restore ./main.vault.backup ./restored.vault
```

Backups are byte-for-byte copies of the encrypted file. They are still sensitive and permit offline password-guessing attempts if the password is weak. Keep backups in a separate protected location and never store the password beside them.

### 7. Configure and query a Bitcoin balance

Networking is disabled by default. First create a non-secret config template:

```bash
vaultsh config-init ./vaultsh.toml
```

Open `vaultsh.toml` and change `network_requests_enabled = false` to `network_requests_enabled = true`. Leave `tor_enabled = false`: this version does not implement Tor transport and refuses to make the balance request if that option is true.

Then provide an Esplora-compatible API endpoint you trust. The example hostname below is reserved for documentation; replace it with your own node or a provider you deliberately choose:

```bash
vaultsh bitcoin balance ADDRESS --endpoint https://esplora.example/api --config ./vaultsh.toml --allow-network
```

The command sends the address to the endpoint using `GET /address/{address}`. Confirmed and net-unconfirmed amounts are displayed in BTC and satoshis. This is data supplied by the selected service, not a cryptographic proof of balance. The request can reveal the address and connection metadata (such as your IP address) to the endpoint operator. Vaultsh does not choose a provider automatically, follow redirects, use environment-configured HTTP proxies, or route this request through Tor. Prefer a self-hosted trusted endpoint where feasible.

### 8. Inspect the application

```bash
vaultsh --help
vaultsh about
vaultsh networks
vaultsh privacy
vaultsh config
vaultsh version
```

Validate a config file with:

```bash
vaultsh config-check ./vaultsh.toml
```

More commands and exact arguments are documented in the [CLI reference](docs/CLI_REFERENCE.md).

## Tests and quality checks

Run from the repository root:

```bash
pytest
pytest --cov=vaultsh --cov-report=term-missing
ruff check .
mypy src/vaultsh
```

Some Bitcoin wallet tests may be skipped if project dependencies have not been installed. Install the project using `python -m pip install -e ".[dev]"` before interpreting test results. Client tests use mocked responses and do not contact a live endpoint. Passing tests do not replace dependency review, platform testing, and an independent security audit.

## Security and privacy

Vaultsh is local-first, but it does **not** guarantee anonymity. Public blockchain activity may be traceable. The balance command discloses the queried address and network metadata to the explicitly selected endpoint. Network requests and telemetry are disabled by default; this command requires both a config setting and `--allow-network`. Remote endpoints must use HTTPS. Redirects and ambient proxy settings are disabled. The command will refuse to connect when `tor_enabled = true`, because it does not yet have a tested Tor transport.

The recovery phrase controls the wallet independently of the vault password. Anyone who obtains it can derive the associated private keys. Python cannot guarantee reliable zeroization of strings and intermediate secret values from memory. Read the [security model](docs/SECURITY_MODEL.md) and [SECURITY.md](SECURITY.md) before experimenting.

**Use synthetic data only. Do not use Vaultsh 0.4.5 with real funds.**

## License

Vaultsh is licensed under **GPL-3.0-only**. See [LICENSE](LICENSE). Third-party dependencies have their own licenses.
