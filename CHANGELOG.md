Changelog
All notable changes to Vaultsh are documented here. This project is in pre-alpha and does not follow a stable-release compatibility promise yet.
[Unreleased]
Added
- Added SECURITY.md guidance for private vulnerability reporting, secret handling, and pre-alpha limitations.
- Added validated, immutable AppConfig settings and a TOML config loader with safe defaults.
- Added a non-secret WalletSummary model with basic field validation.
- Added versioned authenticated encryption for byte payloads using AES-256-GCM and Scrypt through cryptography.
- Added bounded validation of encryption-envelope parameters before running the password KDF.
- Added atomic local file writes for encrypted vault files and encrypted-vault backup/restore helpers.
- Added a derivation-path parser for BIP32-style path syntax. This parses paths only; it does not derive private keys.
- Added a minimal chain-adapter protocol without pretending that chain-specific rules are interchangeable.
- Added explicit network-access policy helpers and disabled-by-default telemetry/network settings.
- Added optional Tor proxy configuration helpers using socks5h URLs to avoid local target-host DNS resolution when used by a compatible client.
- Added reusable Rich status panels and explicit confirmation prompt helpers.
- Expanded CLI commands for project status, supported/planned networks, privacy defaults, and configuration inspection.
- Added 48 unit tests covering CLI output, configuration validation/loading, encryption, vault storage, backup/restore, derivation paths, network policy, Tor proxy configuration, wallet metadata, and UI helpers.
Security notes
- Vaultsh remains pre-alpha and is not suitable for real funds.
- Wallet creation, mnemonic generation/import, blockchain-specific key derivation, signing, balance retrieval, and broadcasting remain unimplemented.
- Tor helpers only describe/configure a proxy; they do not start Tor, verify connectivity, or guarantee anonymity.