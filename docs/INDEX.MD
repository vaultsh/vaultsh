# Vaultsh documentation index

This documentation describes **Vaultsh 0.6.0**. Vaultsh is a pre-alpha Python terminal application, not an audited wallet for real funds.

## User documentation

- [README](../README.md) — overview, install, quick start, status matrix, and security warnings.
- [CLI reference](CLI_REFERENCE.md) — supported commands and options.
- [Configuration](CONFIGURATION.md) — TOML preferences and the dual network permission gate.
- [Network adapters](NETWORK_ADAPTERS.md) — Bitcoin Esplora and EVM JSON-RPC behavior, privacy caveats, and limits.
- [Encrypted vault format](VAULT_FORMAT.md) — encryption envelope, schema v1/v2, and recovery-phrase storage.
- [Security model](SECURITY_MODEL.md) — threat boundaries, known risks, and security release requirements.
- [Roadmap](ROADMAP.md) — implemented work and unimplemented goals.
- [Test results](TEST_RESULTS.md) — actual local test command, result, environment, and skips.

## Maintainer documentation

- [Architecture](ARCHITECTURE.md) — package ownership and dependency direction.
- [Development and testing](DEVELOPMENT.md) — local environment and quality checks.
- [Contributing](../CONTRIBUTING.md) — changelog/commit style, pull-request checklist, and release steps.
- [Security policy](../SECURITY.md) — how to report vulnerabilities safely.
- [Changelog](../CHANGELOG.md) — release history and user-visible changes.

## Current capabilities in 0.6.0

- Encrypted local vault files and encrypted backup/restore.
- Bitcoin Mainnet BIP-39/BIP-84 wallet creation/recovery (limited to the first receiving address in the implemented path).
- Read-only Bitcoin Mainnet balance and first-page address transaction history via a user-selected Esplora endpoint.
- Read-only native-asset balance via a user-selected JSON-RPC endpoint for Ethereum, Polygon PoS, Arbitrum One, Optimism, and Base; each profile has a pinned chain ID.
- Network use requires both TOML permission and `--allow-network`; Tor is not implemented and direct requests are refused when `tor_enabled = true`.

Ethereum private-key derivation and wallet records, ERC-20 balances, Monero, address-gap discovery, transaction previews, signing, and broadcasting are not implemented. See the [roadmap](ROADMAP.md) for the distinction between completed and planned items.
