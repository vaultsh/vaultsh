## 🚀 [1.0.0-beta.1] - 2026-10-27

### ✨ Added

- Added BIP-39 wallet creation/recovery and encrypted-vault records for Bitcoin Mainnet, Ethereum Mainnet, and Solana Mainnet Beta.
- Added local Bitcoin Mainnet P2WPKH transaction signing and Esplora broadcast, using confirmed UTXOs at the first receive address, a visible output/fee preview, a maximum-fee cap, and exact typed confirmation.
- Added local native ETH transaction signing and `eth_sendRawTransaction` broadcast for Ethereum Mainnet only, with chain-ID verification, nonce/gas/balance queries, a maximum-fee cap, and typed confirmation.
- Added local native SOL transaction construction/signing and Solana Mainnet submission using `solders`, Mainnet genesis-hash validation, balance/fee checks, and typed confirmation.
- Added Monero wallet creation/open/close, address and balance lookup, and two-step transfer submission through the official local `monero-wallet-rpc`; transfers are prepared with `do_not_relay` and only relayed after typed confirmation.
- Added Mainnet validation for the current Monero wallet address and corrected the default wallet-RPC port to `127.0.0.1:18082`.
- Added QR display and PNG export for recognized public BTC, EVM, XMR, and SOL address formats; QR input refuses whitespace/recovery phrases and strings that do not resemble supported public addresses.
- Added exact decimal parsing for BTC, ETH, SOL, and XMR; transfer preview objects hide raw signed transaction/Monero metadata from their string representation.
- Added a high-visibility Bitcoin send warning in the CLI for the known first-receive-address/change-discovery limitation.
- Added transfer amount, QR, mainnet validation, Monero relay-metadata, and CLI regression tests. Chain signing tests are dependency-gated where their crypto dependencies are unavailable.
- Added Beta 1.0 docs and translated README files in English, Polish, and Russian.

### 🔄 Changed

- Updated package metadata and runtime version to `1.0.0b1` (human release label: `1.0.0-beta.1`) and marked the project as Beta.
- Updated command help, dashboards, network capability tables, Textual status messages, and all three READMEs to distinguish implemented transfer paths from read-only network profiles.
- Replaced unsupported Textual `@media` CSS with Python-driven responsive class toggling for the overview grid.
- Changed the Monero wallet-RPC default port to the documented local default `18082`; the current wallet address must validate as Mainnet before address/balance display.
- Tightened QR address-format checks and refreshed the security model, CLI reference, network adapter guide, roadmap, changelog, and test report.

### 🧪 Test results

- Latest local run: **194 passed, 7 skipped, 53% line coverage** (1,577/2,986 statements) on Python 3.13.5 / Linux (`python -m pytest --cov=vaultsh --cov-report=term-missing -q`).
- Skips are dependency-gated: Textual UI runtime tests require `textual`; Bitcoin derivation/signing tests require `embit`; EIP-55/ETH-signing tests require `eth-utils` and `eth-account`.
- Unit tests use fake RPC/Esplora responses. No live node/provider was contacted and no real transaction was broadcast during this release preparation.

### 🛡️ Security notes and limitations

- This is a beta release, not an independently audited wallet. Use disposable wallets and small test amounts only; mainnet transfers are irreversible.
- **Bitcoin sending has a known funds-discovery limitation:** only the first receive address is scanned for spendable UTXOs. Change is sent to BIP-84 path `m/84'/0'/0'/1/0`, which the current balance/history/send paths do not scan. As a result, change output may become invisible and cannot be spent through Vaultsh yet. Do not use BTC send with real funds until address/change discovery is implemented and verified.
- Ethereum signing/sending is enabled only for native ETH on chain ID 1, using a legacy `gasPrice` transaction. Other EVM profiles are read-only; ERC-20, EIP-1559, contract calls, token transfers and receipt/finality polling are not implemented.
- Solana support sends native SOL only. SPL tokens, address discovery, transaction history and confirmation/finality polling are not implemented. A successful `sendTransaction` response is submission acknowledgement, not confirmation.
- Monero key/seed handling and signing are performed by the official local `monero-wallet-rpc`, not Vaultsh. Monero wallet files/seeds are outside the Vaultsh encrypted vault. Verify daemon/node configuration and never expose wallet-RPC beyond loopback.
- QR format recognition is not a full checksum verifier for every supported address type. Always compare the decoded QR with the intended public address; QR rejects unrecognized payloads but cannot prove ownership.
- Network access requires both config permission and `--allow-network`; endpoint operators can see queried addresses and connection metadata. Tor transport is not implemented and is refused when `tor_enabled = true`.
- Chain dependencies could not all be imported in the isolated build environment, so signed transaction paths and the Textual runtime were not fully executed here. Tests and successful compilation are not a security certification.

---

## 🚧 [Unreleased]

No unreleased changes have been recorded yet.

## 🚀 [0.9.0] - 2026-10-27

### ✨ Added

- Added a full-screen Textual TUI with Overview, Vault & Wallets, Network, Files, and Settings tabs.
- Added a consistent black-and-orange responsive theme using Textual `Header`, `Footer`, `TabbedContent`, `DataTable`, `Digits`, `DirectoryTree`, `Link`, `Input`, `TextArea`, `Checkbox`, `Select`, `Rule`, buttons, and status panels.
- Added `vaultsh ui` and `vaultsh tui` launch commands. Interactive terminals launch Textual by default; non-interactive/captured runs retain the Rich dashboard.
- Added a dynamic Textual header showing the Vaultsh version, a sanitized local OS username, and network permission/request state (`OFF`, `ARMED`, `REQUESTING`, `RESPONSE`, `ERROR`, or `BLOCKED`).
- Added visual access to local vault creation, encrypted backup/restore, limited offline Bitcoin wallet creation/recovery/listing, read-only network queries, and settings without replacing the existing CLI command paths.
- Added a path navigator which selects paths but does not display or decrypt vault contents, and links to project and upstream documentation.
- Added a single-use network consent checkbox in the TUI; every query still requires the TOML permission and a user-selected endpoint.
- Added headless Textual app tests for all three interface languages, tab mounting, title/state changes, and network-off defaults, plus dependency-free title sanitization tests.
- Added `pytest-asyncio` to development dependencies so Textual's asynchronous test harness can run after dependencies are installed.
- Added `docs/INTERFACE.md` and Polish/Russian translations, and updated the three READMEs, roadmap, development guide, security notes, and test report.

### 🔄 Changed

- Updated package and User-Agent version metadata to `0.9.0`.
- Made Textual the default frontend only for interactive terminals; preserved Rich output for redirected output and automation.
- Improved network status indicators so numeric `Digits` are paired with readable localized status labels.
- Added a missing action to apply the selected path from the Files tab to the vault-path field.
- Updated local testing configuration for automatic asyncio test discovery.

### 🧪 Tests and verification

- Local run: **148 passed, 5 skipped**, with **63% aggregate line coverage** on Python 3.13.5 / Linux (`python -m pytest --cov=vaultsh --cov-report=term-missing -q`).
- The 5 skips are one entire Textual UI test module (Textual is declared but unavailable in this offline environment), three `embit`-dependent Bitcoin derivation tests, and one `eth-utils`-dependent EIP-55 test.
- Python source compilation passed. Network tests use mocked responses; no live provider was contacted.

### 🛡️ Security notes and limitations

- Vaultsh remains pre-alpha, unaudited, and unsuitable for real funds.
- The Textual UI was not runtime-tested in this environment because the Textual package could not be downloaded; its headless tests are included and should run after installing `.[dev]` in a network-enabled environment.
- The header title is Textual's in-app Header title; behavior of the operating-system terminal tab/title bar depends on the terminal emulator.
- The Files tab selects a path only. It does not preview, parse, or reveal vault secrets.
- There is no built-in raster-image widget in the chosen Textual core interface; the dashboard uses a responsive text/ASCII brand mark rather than claiming bitmap scaling support.
- The UI does not implement Tor transport. If `tor_enabled = true`, network requests fail closed. Network requests still require both TOML permission and the per-request checkbox/CLI flag.
- Monero, EVM key management, token balances, transaction construction/signing/broadcasting, full wallet discovery, and independent security review remain out of scope/unimplemented.

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
