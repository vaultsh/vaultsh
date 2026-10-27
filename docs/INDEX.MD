# Vaultsh documentation

Vaultsh is a pre-alpha Python terminal application. This documentation describes the behavior implemented in **version 0.4.5** and distinguishes it from planned features.

## User documentation

- [CLI reference](CLI_REFERENCE.md) — commands, options, prompts, network permissions, and examples.
- [Configuration](CONFIGURATION.md) — TOML settings and privacy-preserving defaults.
- [Encrypted vault format](VAULT_FORMAT.md) — envelope encryption, document schema, and backups.
- [Security model](SECURITY_MODEL.md) — threat boundaries, secret handling, and network privacy.
- [Roadmap](ROADMAP.md) — implemented features versus planned work.

## Maintainer documentation

- [Architecture](ARCHITECTURE.md) — module ownership and dependency direction.
- [Development and testing](DEVELOPMENT.md) — environment setup, quality checks, and test policy.
- [Contributing](../CONTRIBUTING.md) — changes, changelogs, commit style, and pull-request checklist.
- [Security policy](../SECURITY.md) — vulnerability reporting and user responsibilities.
- [Changelog](../CHANGELOG.md) — versioned release history.

## Version and status

Vaultsh 0.4.5 supports encrypted local vaults; offline Bitcoin Mainnet BIP-39/BIP-84 creation and recovery; and a read-only balance query for one user-specified Bitcoin Mainnet address through a user-selected Esplora-compatible endpoint. Network access requires both a configuration setting and `--allow-network`. Remote endpoints must use HTTPS, and the command does not route through Tor.

The implementation does not discover all wallet addresses, aggregate wallet-wide balances, fetch transaction history, construct or sign transactions, broadcast payments, or support Ethereum/EVM or Monero. It has not been independently audited and is not suitable for real funds.
