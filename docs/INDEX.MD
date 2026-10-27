# Vaultsh documentation

Vaultsh is a pre-alpha Python terminal application. This documentation describes the behavior implemented in version 0.3.0 and explicitly separates it from planned work.

## User documentation

- [CLI reference](CLI_REFERENCE.md) — commands, options, prompts, and example workflows.
- [Configuration](CONFIGURATION.md) — TOML settings and privacy-preserving defaults.
- [Encrypted vault format](VAULT_FORMAT.md) — envelope encryption, document schema, and backups.
- [Security model](SECURITY_MODEL.md) — threat boundaries, secret handling, and limitations.
- [Roadmap](ROADMAP.md) — implemented features versus planned work.

## Maintainer documentation

- [Architecture](ARCHITECTURE.md) — module ownership and intended dependency direction.
- [Development and testing](DEVELOPMENT.md) — environment setup, quality checks, and test policy.
- [Contributing](../CONTRIBUTING.md) — changes, changelogs, commit style, and pull-request checklist.
- [Security policy](../SECURITY.md) — vulnerability reporting and user responsibilities.
- [Changelog](../CHANGELOG.md) — versioned release history.

## Version and status

The documented implementation is **Vaultsh 0.3.0**. It supports offline Bitcoin Mainnet BIP-39 phrase generation/recovery and one BIP-84 receive address. It does not query blockchain data or construct/sign/broadcast transactions. It has not been independently audited and is not suitable for real funds.
