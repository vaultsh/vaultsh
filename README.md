<div align="center">

# Vaultsh

### A privacy-focused, self-custodial cryptocurrency wallet for the terminal.

**Private by design. Self-custodial by default. Built for the command line.**

[![License: GPL-3.0-only](https://img.shields.io/badge/License-GPL--3.0--only-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Interface](https://img.shields.io/badge/Interface-CLI-222222.svg)](#technology-stack)
[![Status](https://img.shields.io/badge/Status-Pre--alpha-orange.svg)](#project-status)

</div>

---

## Overview

**Vaultsh** is an open-source, Python-first cryptocurrency wallet project designed for people who prefer a terminal-native workflow and want to retain control over their digital assets.

The long-term goal is to provide a modular, multi-chain wallet for **Windows 10/11, Linux, and Android through Termux**, with a strong focus on self-custody, local data protection, transparent network behavior, and privacy-conscious defaults.

Vaultsh is intended to keep the user in control: no mandatory account, no advertising, no telemetry by default, and no centralized custody of wallet keys.

> [!WARNING]
> **Vaultsh is currently in pre-alpha.** The repository is not a functioning cryptocurrency wallet. A few low-level helpers for authenticated encryption and local file handling exist, but they have not received an independent security audit and are not a complete wallet vault. Wallet/seed generation and recovery, blockchain-specific key derivation, balance retrieval, transaction signing, and transaction broadcasting are not implemented. Do not use it to store or transact real funds.

## Project goals

- **Self-custody:** keep wallet secrets under the user's control rather than relying on a custodial service.
- **Privacy by default:** avoid telemetry, analytics, advertising, and unnecessary data collection.
- **Local-first security:** design for encrypted local storage and user-controlled backups.
- **Multi-chain architecture:** support different blockchain families through isolated, chain-specific adapters.
- **Terminal-native UX:** provide a clear, keyboard-friendly CLI using Rich.
- **Cross-platform portability:** target Windows, Linux, and Termux, subject to platform-specific testing.
- **Transparency:** keep the code open to inspection, testing, and independent security review.
- **Safe transaction handling:** show transaction details clearly and require deliberate confirmation before signing or broadcasting.

## Design principles

### Privacy without false promises

Vaultsh aims to minimize unnecessary data exposure, but **it cannot guarantee complete anonymity**.

Public blockchain activity can be traceable. RPC providers may observe queries and connection metadata, and a network connection may expose information such as an IP address. Tor and self-hosted nodes can reduce certain forms of exposure, but they do not automatically make on-chain activity anonymous.

Privacy features will be documented with their limitations and threat models.

### Self-custody

The intended design keeps private keys and recovery material under the user's control. Vaultsh will not require users to upload seed phrases, private keys, or wallet backups to a Vaultsh-operated server.

### Security-first development

Security-sensitive functionality will be introduced incrementally. Vaultsh will favor established standards, maintained cryptographic libraries, explicit transaction previews, automated tests, and independent review over custom cryptographic implementations.

## Target platforms

| Platform | Target |
|---|---|
| Windows 10 / 11 | Supported target |
| Linux | Supported target |
| Android via Termux | Supported target; device-level compatibility testing required |

Cross-platform support is a development goal, not a claim that every planned feature already works on every platform.

## Technology stack

| Area | Technology | Purpose |
|---|---|---|
| Primary language | **Python 3.12+** | Application logic and cross-platform development |
| CLI framework | **Typer** | Structured commands and argument parsing |
| Terminal UI | **Rich** | Panels, tables, status messages, and readable terminal output |
| Cryptographic primitives | **`cryptography`** | Established cryptographic building blocks where appropriate |
| Packaging | **`pyproject.toml` + Hatchling** | Build configuration and Python package metadata |
| Testing | **pytest** | Unit and integration tests |
| Test coverage | **pytest-cov** | Coverage reporting |
| Linting | **Ruff** | Fast linting and import/style checks |
| Static typing | **mypy** | Static type checking |
| Configuration | **TOML** | Human-readable, non-secret application settings |
| CI | **GitHub Actions (planned)** | Automated checks across supported platforms |

Blockchain-specific dependencies will be selected separately for each integration. The project will avoid adding large or security-sensitive dependencies before their need, maintenance status, licensing, and compatibility have been reviewed.

## Architecture

Vaultsh uses a modular package layout so that the CLI, wallet domain, cryptographic operations, storage, network integrations, and privacy controls remain separate.

```text
vaultsh/
├── pyproject.toml
├── README.md
├── LICENSE
├── SECURITY.md
├── src/
│   └── vaultsh/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── config.py
│       ├── core/
│       │   └── wallet.py
│       ├── crypto/
│       │   ├── encryption.py
│       │   └── derivation.py
│       ├── storage/
│       │   ├── vault.py
│       │   └── backup.py
│       ├── networks/
│       │   ├── base.py
│       │   ├── bitcoin/
│       │   ├── ethereum/
│       │   └── monero/
│       ├── privacy/
│       │   ├── network_policy.py
│       │   └── tor.py
│       └── ui/
│           ├── panels.py
│           └── prompts.py
└── tests/
    ├── test_cli.py
    └── test_config.py
```

Some modules provide limited foundational helpers, while chain adapters and complete wallet workflows remain unimplemented.

### Component responsibilities

- **`cli.py`** — command entry point and user-facing CLI commands.
- **`core/`** — wallet domain models and application workflows.
- **`crypto/`** — narrowly scoped wrappers around reviewed cryptographic primitives and chain-specific derivation standards.
- **`storage/`** — encrypted local vault format, atomic writes, and backup/restore workflows.
- **`networks/`** — blockchain-specific adapters and transaction logic.
- **`privacy/`** — network policy and optional privacy transport integrations.
- **`ui/`** — reusable Rich panels, tables, and confirmation prompts.
- **`tests/`** — automated checks for behavior, regressions, and security-sensitive requirements.

### Multi-chain strategy

Multi-chain support does not mean using one generic signing or key-derivation implementation for every blockchain.

Each network adapter must define and test its own address validation, derivation rules, transaction construction, fee handling, signing, and broadcasting behavior. Shared interfaces will coordinate the adapters without hiding important chain-specific differences.

## Planned features

Features below describe the roadmap. They should not be interpreted as implemented functionality.

- [ ] Rich-based terminal interface
- [ ] Encrypted local wallet vault
- [ ] Password-based protection for local wallet data
- [ ] User-controlled backup and recovery
- [ ] Multi-chain adapter architecture
- [ ] Public-address validation
- [ ] Read-only balance and transaction-history queries
- [ ] Transaction preview and explicit confirmation
- [ ] Chain-specific transaction signing and broadcasting
- [ ] Configurable RPC endpoints and self-hosted node support
- [ ] Optional Tor integration
- [ ] Offline transaction preparation/signing workflow
- [ ] Automated testing on Windows and Linux
- [ ] Termux installation and compatibility testing
- [ ] Dependency review and independent security audit

## Roadmap

### Phase 1 — Project foundation
- [x] Initial Python package layout
- [x] Typer/Rich CLI scaffold
- [x] Basic tests and development tooling configuration
- [ ] Threat model and contribution guidelines
- [ ] CI pipeline and dependency review

### Phase 2 — Secure local storage
- [ ] Define a versioned vault file format
- [ ] Choose and document password-based key derivation parameters
- [ ] Implement authenticated encryption using established primitives
- [ ] Add atomic file writes and corruption handling
- [ ] Test backup and restore flows
- [ ] Verify that secrets never enter logs or error reports

### Phase 3 — First blockchain integration
- [ ] Select the first chain and supported wallet standards
- [ ] Implement read-only address and balance operations
- [ ] Add chain-specific key management and recovery
- [ ] Implement transaction previews and signing
- [ ] Add official test vectors and edge-case tests
- [ ] Review the implementation before any real-funds use

### Phase 4 — Privacy and additional chains
- [ ] Add configurable network endpoints
- [ ] Document self-hosted node setup
- [ ] Implement and test optional Tor support
- [ ] Add further chain adapters independently
- [ ] Test network behavior and metadata exposure

### Phase 5 — Release hardening
- [ ] Windows, Linux, and Termux compatibility testing
- [ ] Automated release checks
- [ ] Dependency and license audits
- [ ] Independent security review
- [ ] Documented stable-release criteria

## Getting started

### Requirements

- Python 3.12 or newer
- `pip`
- Git (optional, for cloning the repository)

### 1. Clone the repository

Replace the placeholder URL with the actual repository URL:

```bash
git clone <YOUR_REPOSITORY_URL>
cd vaultsh
```

### 2. Create a virtual environment

**Windows PowerShell**

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / Termux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install the development version

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Termux may require platform-specific setup for some dependencies. Validate installation on the target device before relying on it.

### 4. Run Vaultsh

```bash
vaultsh
```

You can also run:

```bash
python -m vaultsh
```

The current scaffold provides basic informational commands:

```bash
vaultsh about
vaultsh networks
vaultsh version
```

These commands do not create wallets or perform blockchain operations.

### 5. Run tests and quality checks

```bash
pytest
ruff check .
mypy src/vaultsh
```

## Security

Vaultsh is experimental software and has not undergone an independent security audit.

Until the relevant features are implemented and reviewed:

- Do not use the scaffold to store real funds.
- Do not enter a real recovery phrase or private key into unimplemented commands.
- Never commit secrets, wallet files, recovery phrases, or backups to version control.
- Never send private keys or recovery phrases to RPC endpoints or third-party services.
- Verify destination addresses, networks, amounts, and fees before signing transactions.
- Use a dedicated private channel to report security vulnerabilities once one is established.

See [`SECURITY.md`](SECURITY.md) for the project's initial security policy.

## Contributing

Contributions, issue reports, design reviews, and documentation improvements are welcome.

Before submitting a pull request:

1. Explain the change and its motivation.
2. Add or update tests where appropriate.
3. Run `pytest`, `ruff check .`, and `mypy src/vaultsh`.
4. Do not include secrets or personal wallet data in examples, tests, logs, or screenshots.
5. For cryptographic or transaction changes, document the relevant standards and test vectors.

Security-sensitive changes should receive additional review before being merged.

## License

Vaultsh is licensed under the **GNU General Public License v3.0 only (GPL-3.0-only)**.

You may use, study, modify, and redistribute the project under the terms of that license. When distributing covered modified versions, you must comply with the applicable GPL requirements, including source-code availability obligations.

See [`LICENSE`](LICENSE) for the complete license text.

Third-party dependencies remain subject to their own licenses.

## Disclaimer

Vaultsh is software under development and is provided without warranties, to the extent permitted by applicable law. It is not financial advice. Cryptocurrency transactions can be irreversible, and software defects or compromised devices can result in permanent loss of funds.

Users are responsible for evaluating risks and protecting their devices, credentials, and backups.

---

<div align="center">

**Vaultsh — Your keys. Your terminal. Your control.**

</div>
