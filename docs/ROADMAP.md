# Roadmap

This is a directional plan, not a promise that a feature is safe or scheduled for a particular release. The project remains pre-alpha and must not be used with real funds.

## Current baseline: 0.3.0

- [x] Typer/Rich terminal interface.
- [x] Validated non-secret TOML settings with privacy-preserving defaults.
- [x] Password-derived encryption envelope using Scrypt and AES-256-GCM.
- [x] Encrypted local vault file with versioned inner document.
- [x] Encrypted byte-for-byte backup and restore.
- [x] Read/validate schema v1 metadata-only vaults.
- [x] Store schema v2 Bitcoin wallet records inside the encrypted payload.
- [x] Generate/recover English BIP-39 phrases (12 words generated; 12 or 24 accepted for recovery).
- [x] Derive the first Bitcoin Mainnet BIP-84 Native SegWit receiving address.
- [x] List public wallet metadata without returning recovery phrases.

## Near-term candidates

1. **Release quality and docs:** complete platform CI, ensure `embit` test vectors run in CI, run Ruff/mypy, add a package build check, and keep documentation aligned with actual commands.
2. **Read-only Bitcoin data:** after a privacy and API design review, add an explicitly configured node or RPC client, address discovery with gap-limit handling, and balances/history clearly labeled as externally sourced.
3. **Transport privacy:** define a testable transport interface, support explicit proxy configuration, and verify no direct-connect fallback when Tor transport is requested. Do not claim Tor support until real traffic is demonstrably routed and tested.
4. **Transaction preparation:** introduce a human-readable transaction preview, fee/UTXO policy, and strict address/network validation before any signing implementation.
5. **Signing design:** obtain independent review of key custody, PSBT handling, change-address logic, network selection, fee handling, and signing before implementing transaction signing or broadcasting.

## Multi-chain direction

Ethereum/EVM and Monero need separate adapter designs and well-defined cryptographic/key-derivation rules. Adding a folder or a generic interface is not the same as implementing a wallet. Each chain requires official vectors, tests, network-specific threat analysis, and separate documentation.

## Release gates before real funds

No real-funds release should be considered until the project has independent security review, dependency/supply-chain review, platform CI, comprehensive malformed-input tests, tested recovery workflows, careful release packaging, and a documented disclosure channel. A high test count alone is not a security certification.
