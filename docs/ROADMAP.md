# Roadmap

This is a directional plan, not a promise that a feature is safe or scheduled for a particular release. The project remains pre-alpha and must not be used with real funds.

## Current baseline: 0.4.5

- [x] Typer/Rich terminal interface.
- [x] Validated non-secret TOML settings with privacy-preserving defaults.
- [x] Password-derived encryption envelope using Scrypt and AES-256-GCM.
- [x] Encrypted local vault file with versioned inner document.
- [x] Encrypted byte-for-byte backup and restore.
- [x] Read/validate schema-v1 metadata-only vaults and store schema-v2 Bitcoin wallet records.
- [x] Generate/recover English BIP-39 phrases (12 words generated; 12 or 24 accepted for recovery).
- [x] Derive the first Bitcoin Mainnet BIP-84 Native SegWit receiving address.
- [x] List public wallet metadata without returning recovery phrases.
- [x] Query confirmed and net-unconfirmed statistics for one user-supplied Bitcoin Mainnet address through an explicit Esplora endpoint.
- [x] Require configuration permission and `--allow-network`; disable redirects and environment proxies; bound API response size and timeout.
- [x] Refuse a balance lookup when Tor is enabled in config but no Tor transport is implemented.

## Near-term candidates

1. **Release quality:** complete platform CI, ensure `embit` test vectors run in CI, run Ruff/mypy, add a package build check, dependency auditing, and validate release artifacts.
2. **Address discovery and wallet-wide accounting:** derive a documented range of receive/change addresses, apply a tested gap-limit policy, and aggregate balances/history without falsely presenting a single-address result as a whole-wallet total.
3. **Node support and transport privacy:** evaluate a local Bitcoin Core RPC client and harden workflows for self-hosted Esplora endpoints. Add a testable transport abstraction only when redirect/proxy behavior, connection policy, and errors are covered. Do not claim Tor support until requests are demonstrably routed through it without direct-connect fallback.
4. **Transaction preparation:** introduce human-readable transaction preview, fee/UTXO policy, change handling, and strict network/address validation before signing.
5. **Signing design:** obtain independent review of key custody, PSBT handling, change-address logic, network selection, fee handling, and signing before implementing signing or broadcasting.

## Multi-chain direction

Ethereum/EVM and Monero need separate adapter designs and well-defined cryptographic/key-derivation rules. Adding a folder or a generic interface is not the same as implementing a wallet. Each chain requires official vectors, tests, network-specific threat analysis, and separate documentation.

## Release gates before real funds

No real-funds release should be considered until the project has independent security review, dependency/supply-chain review, platform CI, comprehensive malformed-input tests, tested recovery workflows, careful release packaging, and a documented disclosure channel. A high test count alone is not a security certification.
