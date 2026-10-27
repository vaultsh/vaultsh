# Changelog

All notable changes to Vaultsh are recorded here. Vaultsh is pre-alpha; a version number does not imply production readiness, an audit, or a stable compatibility promise. Dates use `YYYY-MM-DD`.

## 🚧 [Unreleased]

No unreleased changes yet.

## 🚀 [0.6.0] - 2026-10-27

### ✨ Added

- Added read-only Bitcoin Mainnet address transaction history through a user-selected Esplora-compatible endpoint using `GET /address/{address}/txs`.
- Added `vaultsh bitcoin history ADDRESS --endpoint URL --config PATH --allow-network [--limit 1..25]` with transaction ID, confirmation state, block metadata, and provider-supplied fee where available.
- Added a bounded newest-first result page for a single Bitcoin address and validation of txids, status fields, confirmed-block metadata, duplicate entries, and optional fee values.
- Added read-only native-asset balance queries for five explicit EVM mainnets through a user-selected JSON-RPC 2.0 endpoint: Ethereum Mainnet (chain ID `1`, ETH), Polygon PoS Mainnet (`137`, POL), Arbitrum One (`42161`, ETH), Optimism Mainnet (`10`, ETH), and Base Mainnet (`8453`, ETH).
- Added `vaultsh evm balance ADDRESS --chain NETWORK --endpoint URL --config PATH --allow-network`, while retaining `vaultsh ethereum balance` as the Ethereum Mainnet-specific shortcut.
- Added profile-specific `eth_chainId` checks that reject endpoints unless they return the selected network ID before a balance query is made.
- Added `eth_getBalance` response/request ID validation and integer-based wei-to-ETH formatting without floating-point arithmetic.
- Added EVM 20-byte hexadecimal address validation and EIP-55 checksum validation for mixed-case addresses using `eth-utils`.
- Added request body size limits, timeouts, redirect rejection, explicit HTTPS/loopback-HTTP endpoint policy, and disabled environment-proxy discovery for EVM JSON-RPC requests.
- Added mocked, offline unit tests for EVM RPC parsing/chain ID/address/endpoint behavior, each supported network profile, Bitcoin address-history parsing, and CLI network opt-in.
- Added a GitHub Actions test workflow for Windows/Linux across supported Python versions.
- Added a release test report: the local run completed with 139 passed, 4 dependency-gated skips, and 81% measured line coverage; this is not a hosted CI result or security certification.
- Added `docs/NETWORK_ADAPTERS.md` and `docs/TEST_RESULTS.md`, and expanded the architecture, CLI, configuration, security, development, and roadmap documentation.

### 🔄 Changed

- Updated package version metadata and User-Agent values to `0.6.0`.
- Expanded `vaultsh networks`, `about`, the landing screen, and `privacy` output to distinguish Bitcoin and five EVM read-only query profiles from unimplemented wallet/signing capabilities.
- Kept both TOML permission (`network_requests_enabled = true`) and the CLI flag (`--allow-network`) mandatory for every network query.
- Changed Bitcoin balance output to show the selected endpoint's host rather than echo the full URL path, which may contain a path-based provider token.
- Added `eth-utils` and `eth-hash[pycryptodome]` for EVM mixed-case EIP-55 checksum validation.
- Updated README, CLI/config references, network adapter guidance, vault format notes, security model, roadmap, contributing instructions, and release test reporting.

### 🛡️ Security notes and limitations

- Vaultsh remains pre-alpha and unaudited; do not use this build to store or transact real funds.
- EVM support is read-only native-asset balance lookup for the five listed mainnets. EVM wallet creation/recovery, private-key storage, ERC-20 balances, EVM transaction history, transaction previews, signing, and broadcasting are not implemented.
- Monero is not implemented. The supported EVM profile allow-list does not imply support for other EVM-compatible chains.
- Bitcoin balance/history are limited to one address. History shows at most 25 entries from the first provider response page; it is not complete wallet history and does not discover additional addresses.
- Balance and history output is provider-supplied data and is not an independently verified cryptographic proof. The endpoint receives the queried public address and connection metadata.
- Every network call requires configuration permission and `--allow-network`. Remote endpoints require HTTPS; HTTP is restricted to loopback. Redirects and environment proxy discovery are disabled.
- Tor transport is not implemented. If `tor_enabled = true`, network queries refuse to connect rather than make a direct connection while implying Tor protection.
- Tests use mocked network responses. Local tests that require `embit` or `eth-utils` skip if those dependencies are unavailable; see `docs/TEST_RESULTS.md`. No independent security audit has taken place.

## 🚀 [0.4.5] - 2026-10-27

### ✨ Added

- Added an opt-in, read-only Bitcoin Mainnet balance lookup using a user-selected Esplora-compatible REST endpoint (`GET /address/{address}`).
- Added `vaultsh bitcoin balance ADDRESS --endpoint URL --config PATH --allow-network`.
- Added exact satoshi arithmetic and BTC formatting without floating-point calculations, including separate confirmed and net-unconfirmed values.
- Added endpoint validation: HTTPS is required for remote endpoints; HTTP is accepted only for localhost or loopback IP addresses.
- Added URL checks that reject embedded credentials, query strings, fragments, malformed ports, and dot-segment paths.
- Added a bounded response size, request timeout, JSON/statistics schema validation, response-address matching, and clear handling for HTTP/network failures.
- Added a no-redirect HTTP handler and disabled ambient environment proxy discovery for this client.
- Added offline unit tests for Esplora response parsing, balance calculations, URL policy, malformed input, size limits, opt-in policy, and CLI output.

### 🔄 Changed

- Updated package/runtime version metadata to `0.4.5`.
- Updated the landing screen, `about`, `networks`, and `privacy` commands to describe read-only balance lookup without implying transaction functionality or Tor support.
- Enforced both configuration permission (`network_requests_enabled = true`) and explicit command-line intent (`--allow-network`) before constructing the network client.
- Made the balance command refuse to connect when `tor_enabled = true`, because actual Tor transport is not implemented.
- Updated README, CLI reference, configuration guidance, architecture, roadmap, security policy, and security model.

### 🛡️ Security notes and limitations

- The release was pre-alpha, unaudited, and unsuitable for real funds.
- A balance query disclosed the requested public address and connection metadata to the selected endpoint. The client did not select a default public provider, follow redirects, or honor environment proxy variables.
- The response was third-party/node-provided data, not a cryptographic proof of balance or ownership.
- The command queried one explicitly provided address only. It did not discover all wallet addresses, apply a gap limit, aggregate a wallet balance, or fetch transaction history.
- Transaction construction, PSBT handling, signing, and broadcasting remained unimplemented. Ethereum/EVM and Monero remained unimplemented.

## 🚀 [0.3.0] - 2026-10-27

### ✨ Added

- Added offline Bitcoin Mainnet wallet creation from 128 bits of operating-system entropy using a 12-word English BIP-39 phrase.
- Added BIP-84 Native SegWit first receive-address derivation at `m/84'/0'/0'/0/0`, delegated to the `embit` library.
- Added recovery of a Bitcoin wallet from a valid 12- or 24-word English BIP-39 phrase (empty BIP-39 passphrase only).
- Added `vaultsh wallet create`, `wallet recover`, `wallet list`, and `wallet recovery-phrase` commands.
- Added schema-v2 encrypted wallet records. Recovery phrases remain inside the authenticated encrypted vault payload; normal listing only displays public metadata.
- Added backward-compatible reading of schema-v1 metadata-only vaults. Adding a wallet upgrades a v1 vault to schema v2 through an atomic encrypted replacement.
- Added duplicate-wallet detection, wallet-record validation, explicit confirmation before showing a recovery phrase, and a BIP-84 address-vector test.
- Added wallet storage and CLI regression tests, including checks that recovery phrases are not present in raw encrypted file bytes.

### 🔄 Changed

- Updated package version to `0.3.0` and added `embit>=0.8.0,<0.9` for Bitcoin-specific BIP-39/BIP-32/address derivation.
- Updated the `about`, `networks`, and landing-screen output to distinguish offline Bitcoin derivation from unavailable blockchain and transaction features.
- Updated README, security notes, and installation examples.

### 🛡️ Security notes and limitations

- This was not an audited wallet and was not suitable for real funds.
- The implementation derived only the first Bitcoin Mainnet Native SegWit receiving address. It did not scan the blockchain, discover used addresses, query balances, estimate fees, construct/sign transactions, or broadcast them.
- Only English BIP-39 12- and 24-word phrases were supported. The optional BIP-39 passphrase was not supported; wallets using a non-empty passphrase derive different keys and addresses.
- The phrase was stored inside the encrypted vault and displayed at creation. The vault password and recovery phrase needed separate protection.
- Schema-v1 vaults remained readable. Opening or checking a vault did not migrate it; adding a wallet changed it to schema v2.
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
- Backups remained encrypted, but anyone who obtained one could attempt offline password guessing.
- Wallet creation/recovery, chain-specific key derivation, address generation, balance retrieval, signing, and transaction broadcasting were not implemented.
- Tor support remained configuration-only and did not start Tor or guarantee anonymity.

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
