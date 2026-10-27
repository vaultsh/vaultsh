# Changelog

All notable changes to Vaultsh are documented here. The project is pre-alpha; releases do not imply production readiness or a stable compatibility promise. Dates use `YYYY-MM-DD`.

## 🚧 [Unreleased]

### ✨ Added
- Add a full documentation set covering architecture, CLI commands, configuration, vault format, security, development, roadmap, and contribution workflow.
- Add commit-message examples and a consistent emoji vocabulary for repository updates.

### 📝 Documentation
- Expand the README with a documentation index, installation steps, quick-start commands, feature boundaries, and links to detailed reference pages.

## 🚀 [0.3.0] - 2026-10-27

### ✨ Added
- Added offline Bitcoin Mainnet wallet creation from 128 bits of operating-system entropy using a 12-word English BIP-39 phrase.
- Added BIP-84 Native SegWit first receive-address derivation at `m/84'/0'/0'/0/0`, delegated to the `embit` library.
- Added recovery of a Bitcoin wallet from a valid 12- or 24-word English BIP-39 phrase (empty BIP-39 passphrase only).
- Added `vaultsh wallet create`, `wallet recover`, `wallet list`, and `wallet recovery-phrase` commands.
- Added schema-v2 encrypted wallet records. Recovery phrases remain inside the authenticated encrypted vault payload; normal listing only displays public metadata.
- Added backward-compatible reading of schema-v1 metadata-only vaults. Adding a wallet upgrades a v1 vault to schema v2 through an atomic encrypted replacement.
- Added duplicate-wallet detection, wallet-record validation, explicit confirmation before showing a recovery phrase, and a BIP-84 official address-vector test.
- Added wallet storage and CLI regression tests, including checks that recovery phrases are not present in the raw encrypted file bytes.

### 🔄 Changed
- Updated version metadata to `0.3.0` and added `embit>=0.8.0,<0.9` for Bitcoin-specific BIP-39/BIP-32/address derivation.
- Updated the `about`, `networks`, and landing-screen output to distinguish implemented offline Bitcoin derivation from unavailable blockchain and transaction features.
- Updated README, security notes, and installation examples.

### 🛡️ Security notes and limitations
- This is not an audited wallet. Do not use this pre-alpha build to store or transact real funds.
- The implementation derives only the first Bitcoin Mainnet Native SegWit receiving address. It does not scan the blockchain, discover used addresses, query balances, estimate fees, construct/sign transactions, or broadcast them.
- Only English BIP-39 12- and 24-word phrases are supported. The optional BIP-39 passphrase is not supported; recovery phrases imported from wallets using a non-empty passphrase will derive a different address.
- The phrase is stored inside the encrypted vault and displayed at creation. The vault password and recovery phrase must be protected separately; anyone who obtains the phrase can control the associated wallet.
- Schema-v1 vaults remain readable. There is no automatic migration merely from opening or checking a vault; adding a wallet changes it to schema v2.
- The `embit` library and the complete Vaultsh secret-handling workflow have not received an independent security audit as part of this project.
- Ethereum/EVM, Monero, network/RPC access, Tor transport, balances, signing, and broadcasting remain unimplemented.

## 🚀 [0.2.0] - 2026-10-27

### ✨ Added
- Added a versioned JSON metadata document (`vaultsh.vault`, schema v1) stored inside the encrypted container.
- Added `vaultsh vault init` to create an encrypted, empty metadata container using hidden password prompts and password confirmation.
- Added `vaultsh vault check` to decrypt the container, validate its metadata schema, and display only public metadata.
- Added a minimum 12-character password requirement for creating new vault documents.
- Added `vaultsh vault backup` and `vaultsh vault restore` commands for encrypted, byte-for-byte copies.
- Added `vaultsh config-init` and `vaultsh config-check` for creating and validating non-secret TOML settings.
- Added CLI regression tests for vault lifecycle, password mismatch, overwrite protection, configuration commands, and metadata validation.

### 🔄 Changed
- Updated the start screen and `about` output to describe current local-container functionality and its limitations.
- Updated package metadata and the runtime version constant to `0.2.0`.

### 🛡️ Security notes and limitations
- The initial vault document held metadata and an empty `wallets` list; it did not store wallet secrets.
- Password prompts were hidden, but the encryption format and implementation had not received an independent security audit.
- Backups remained encrypted, but anyone who obtained one could attempt offline password guessing. A unique, high-entropy password and secure backup storage were recommended.
- Wallet creation/recovery, chain-specific key derivation, address generation, balance retrieval, signing, and transaction broadcasting were not implemented in this version.
- Tor support remained configuration-only. It did not start Tor or guarantee anonymity.

## 🚀 [0.1.0] - 2026-10-27

### ✨ Added
- Added the initial pre-alpha project structure and Typer/Rich terminal interface.
- Added configuration models and TOML validation with privacy-preserving defaults.
- Added an authenticated-encryption helper using Scrypt key derivation and AES-256-GCM.
- Added local encrypted-byte storage, atomic file writes, and encrypted backup/restore primitives.
- Added a BIP32-style derivation-path parser without private-key derivation.
- Added network-policy helpers, Tor SOCKS proxy settings, Rich UI helpers, and foundational tests.

### 🛡️ Security notes and limitations
- This was an experimental foundation, not a complete cryptocurrency wallet.
- Wallet generation, blockchain communication, transaction signing, and broadcasting were not implemented.
- No release in the 0.1.x line received an independent security audit.
