# Changelog

All notable changes to Vaultsh are documented here. The project is pre-alpha; a version number does not imply production readiness, an audit, or a stable compatibility promise. Dates use `YYYY-MM-DD`.

## 🚧 [Unreleased]

No unreleased changes yet.

## 🚀 [0.4.5] - 2026-10-27

### ✨ Added

- Added an opt-in, read-only Bitcoin Mainnet balance lookup using a user-selected Esplora-compatible REST endpoint (`GET /address/{address}`).
- Added `vaultsh bitcoin balance ADDRESS --endpoint URL --config PATH --allow-network`.
- Added exact satoshi arithmetic and BTC formatting without floating-point calculations, including separate confirmed and net-unconfirmed values.
- Added endpoint validation: HTTPS is required for remote endpoints; HTTP is accepted only for localhost or loopback IP addresses.
- Added URL checks that reject embedded credentials, query strings, fragments, malformed ports, and dot-segment paths.
- Added a bounded response size, request timeout, JSON/statistics schema validation, response-address matching, and clear handling for HTTP/network failures.
- Added a no-redirect HTTP handler and disabled ambient environment proxy discovery for this client so requests do not silently change hosts or use an unreviewed environment proxy.
- Added offline unit tests for Esplora response parsing, balance calculations, URL policy, malformed input, size limits, opt-in policy, and CLI output.

### 🔄 Changed

- Updated package/runtime version metadata to `0.4.5`.
- Updated the landing screen, `about`, `networks`, and `privacy` commands to describe read-only balance lookup without implying transaction functionality or Tor support.
- Enforced both configuration permission (`network_requests_enabled = true`) and explicit command-line intent (`--allow-network`) before constructing the network client.
- Made the balance command refuse to connect when `tor_enabled = true`, because actual Tor transport is not implemented; it does not silently fall back to a direct connection.
- Updated README, CLI reference, configuration guidance, architecture, roadmap, security policy, and security model.

### 🛡️ Security notes and limitations

- Vaultsh remains pre-alpha, unaudited, and unsuitable for real funds.
- A balance query discloses the requested public address and connection metadata (potentially including the client's IP address) to the user-selected endpoint. Prefer a trusted self-hosted endpoint and understand the provider's privacy policy.
- The client does not select a default public provider, follow HTTP redirects, or honor `HTTP_PROXY`/`HTTPS_PROXY` environment variables. It makes a direct HTTPS request to the configured host; Tor transport is not supported.
- The response is third-party/node-provided data, not a cryptographic proof of balance or ownership. Incorrect, stale, incomplete, or malicious endpoint data remains possible.
- The command queries one explicitly provided address only. It does not discover all wallet addresses, apply a gap limit, aggregate a wallet balance, or fetch transaction history.
- Transaction construction, PSBT handling, signing, and broadcasting remain unimplemented. Ethereum/EVM and Monero remain unimplemented.
- The `embit` dependency and the complete Vaultsh secret-handling workflow have not received an independent security audit as part of this release.

## 🚀 [0.3.0] - 2026-10-27

### ✨ Added

- Added offline Bitcoin Mainnet wallet creation from 128 bits of operating-system entropy using a 12-word English BIP-39 phrase.
- Added BIP-84 Native SegWit first receive-address derivation at `m/84'/0'/0'/0/0`, delegated to the `embit` library.
- Added recovery of a Bitcoin wallet from a valid 12- or 24-word English BIP-39 phrase (empty BIP-39 passphrase only).
- Added `vaultsh wallet create`, `wallet recover`, `wallet list`, and `wallet recovery-phrase` commands.
- Added schema-v2 encrypted wallet records. Recovery phrases remain inside the authenticated encrypted vault payload; normal listing only displays public metadata.
- Added backward-compatible reading of schema-v1 metadata-only vaults. Adding a wallet upgrades a v1 vault to schema v2 through an atomic encrypted replacement.
- Added duplicate-wallet detection, wallet-record validation, explicit confirmation before showing a recovery phrase, and a BIP-84 official address-vector test.
- Added wallet storage and CLI regression tests, including checks that recovery phrases are not present in raw encrypted file bytes.

### 🔄 Changed

- Updated version metadata to `0.3.0` and added `embit>=0.8.0,<0.9` for Bitcoin-specific BIP-39/BIP-32/address derivation.
- Updated the `about`, `networks`, and landing-screen output to distinguish offline Bitcoin derivation from unavailable blockchain and transaction features.
- Updated README, security notes, and installation examples.

### 🛡️ Security notes and limitations

- This was not an audited wallet. It must not be used to store or transact real funds.
- The implementation derived only the first Bitcoin Mainnet Native SegWit receiving address. It did not scan the blockchain, discover used addresses, query balances, estimate fees, construct/sign transactions, or broadcast them.
- Only English BIP-39 12- and 24-word phrases were supported. The optional BIP-39 passphrase was not supported; wallets using a non-empty passphrase derive different keys and addresses.
- The phrase was stored inside the encrypted vault and displayed at creation. The vault password and recovery phrase needed separate protection; anyone who obtained the phrase could control the associated wallet.
- Schema-v1 vaults remained readable. Opening or checking a vault did not migrate it; adding a wallet changed it to schema v2.
- The `embit` library and complete secret-handling workflow had not received an independent security audit.
- Ethereum/EVM, Monero, network/RPC access, Tor transport, balances, signing, and broadcasting were unimplemented.

## 🚀 [0.2.0] - 2026-10-27

### ✨ Added

- Added a versioned JSON metadata document (`vaultsh.vault`, schema v1) stored inside an encrypted container.
- Added `vaultsh vault init` to create an encrypted empty metadata container using hidden password prompts and password confirmation.
- Added `vaultsh vault check` to decrypt the container, validate its metadata schema, and display public metadata.
- Added a minimum 12-character password requirement for creating new vault documents.
- Added `vaultsh vault backup` and `vaultsh vault restore` commands for encrypted, byte-for-byte copies.
- Added `vaultsh config-init` and `vaultsh config-check` for creating and validating non-secret TOML settings.
- Added CLI regression tests for vault lifecycle, password mismatch, overwrite protection, configuration commands, and metadata validation.

### 🔄 Changed

- Updated the start screen and `about` output to describe local-container functionality and its limitations.
- Updated package metadata and the runtime version constant to `0.2.0`.

### 🛡️ Security notes and limitations

- The vault document held metadata and an empty `wallets` list; it did not store wallet secrets.
- Password prompts were hidden, but the encryption format and implementation had not received an independent audit.
- Backups remained encrypted, but anyone who obtained one could attempt offline password guessing. A unique, high-entropy password and protected backup storage were recommended.
- Wallet creation/recovery, chain-specific key derivation, address generation, balance retrieval, signing, and transaction broadcasting were not implemented.
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
