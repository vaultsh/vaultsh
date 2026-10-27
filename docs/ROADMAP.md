# Roadmap

This is a directional roadmap, not a promise of delivery dates. Vaultsh **0.6.0 remains pre-alpha** and must not be used with real funds.

## Current baseline: 0.6.0

- [x] Typer/Rich terminal interface and versioned command groups.
- [x] Validated non-secret TOML config; telemetry and network requests default off.
- [x] Password-derived encrypted envelope using Scrypt and AES-256-GCM.
- [x] Encrypted local vault documents with schema-v1 reading and schema-v2 Bitcoin wallet records.
- [x] Encrypted byte-for-byte backup and restore flows.
- [x] Bitcoin Mainnet BIP-39/BIP-32/BIP-84 offline wallet creation/recovery for a limited first receive address.
- [x] Bitcoin Mainnet address-balance query through explicitly selected Esplora.
- [x] Bitcoin Mainnet first-page address transaction history query, limited to 25 entries.
- [x] Read-only native asset balance queries for Ethereum, Polygon PoS, Arbitrum One, Optimism, and Base through explicitly selected JSON-RPC with chain-ID pinning.
- [x] EVM `eth_chainId` validation against the selected profile before querying a native balance.
- [x] EVM address syntax validation and EIP-55 checksum check for mixed-case addresses.
- [x] Dual network opt-in (`network_requests_enabled = true` and `--allow-network`) with explicit endpoint choice.
- [x] Redirect blocking, direct-connection behavior, timeouts, response-size limits, response-schema validation, and sanitized provider errors.
- [x] Network-client tests built on mocked responses, including network opt-in tests.
- [x] Architecture, CLI, config, network-adapter, security, development, changelog, and contribution docs.
- [ ] CI results for Windows and Linux confirmed on the hosted runner; local CI configuration alone is not proof of success.
- [ ] Run all official Bitcoin and EIP-55 vectors in an environment with every runtime dependency installed; local missing-dependency skips remain documented.
- [ ] Independent security and dependency review.

## Phase 1 — Project foundation

- [x] Initial Python package layout and Typer/Rich CLI.
- [x] Basic tests and development-tool configuration.
- [x] Non-secret TOML template and validation commands.
- [x] Threat model, contribution guidelines, and documentation index.
- [ ] Hosted CI pipeline exercised successfully on Windows/Linux and maintained as a release gate.
- [ ] Automated dependency/license audit and release provenance.

## Phase 2 — Secure local storage

- [x] Versioned metadata document format inside an encrypted envelope.
- [x] Scrypt parameter validation and AES-256-GCM authenticated encryption helper.
- [x] Atomic file writes, malformed-data handling, and encrypted backup/restore tests.
- [x] Limited Bitcoin wallet records with recovery material inside the encrypted payload.
- [ ] Independent review of encryption format, secret handling, and backup/restore behavior.
- [ ] Add a migration/export strategy before broadening the encrypted wallet schema to multiple chain families.

## Phase 3 — First blockchain integration

- [x] Select Bitcoin Mainnet and BIP-39/BIP-84 as the first offline wallet flow.
- [x] Address-scoped Bitcoin Mainnet balance lookup and first-page transaction history.
- [x] Read-only EVM native-asset balance lookup for five explicit mainnet profiles.
- [x] Basic address validation and official-vector-style tests included in the repository.
- [ ] Bitcoin address discovery, gap-limit handling, change-address tracking, and complete wallet-wide balance/history.
- [ ] EVM wallet creation/recovery, private-key handling, and secure vault records.
- [ ] ERC-20 token balances and EVM transaction history.
- [ ] Human-readable transaction preview, fee/gas calculation, transaction building, and offline signing design.
- [ ] Independent review before any real-funds use.

## Phase 4 — Privacy and additional chains

- [x] User-configurable endpoint selection for Esplora and EVM JSON-RPC.
- [x] Document self-hosted endpoint expectations and network metadata exposure.
- [ ] Implement and test genuine Tor transport; do not treat the settings flag as support.
- [ ] Add Monero with its own key/address/view-key privacy model and official test vectors.
- [ ] Add further EVM networks only after chain IDs, native-asset semantics, endpoint requirements, and tests are explicit.
- [ ] Test network behavior against controlled local nodes and realistic hostile responses.

## Phase 5 — Release hardening

- [ ] Automated Windows, Linux, and Android/Termux compatibility testing.
- [ ] Hosted CI and release checks proven on supported runtimes.
- [ ] Dependency, license, and supply-chain audits.
- [ ] Independent security review/audit.
- [ ] Documented stable-release criteria and responsible disclosure workflow.

## Release gates before real funds

Do not treat a high test count or an incremented version number as evidence that funds are safe. A future stable release requires reviewed key custody and recovery, complete wallet address discovery, audited transaction construction/signing, platform validation, robust backups, independent security review, and a documented release process.
