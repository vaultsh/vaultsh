# Security policy

Vaultsh is a **pre-alpha, unaudited project**. Do not use it to store or transact real funds.

## Reporting a vulnerability

Do not put exploitable details, live recovery phrases, passwords, private keys, wallet files, or backups in a public issue. If a private security contact or repository security-advisory channel has been configured for the copy of Vaultsh you use, send the report there. If no private channel exists, contact the maintainers through the trusted project-maintainer channel before publishing technical details; do not assume an address or identity that is not listed by the project.

A useful report includes:

- Affected version/commit and operating system/Python version.
- A concise impact statement and reproducible steps using synthetic data.
- Whether the issue involves data confidentiality, integrity, network privacy, availability, or packaging.
- A suggested mitigation, if known.

Redact endpoints that contain access tokens and use only synthetic vaults/phrases in test cases.

## Scope notes

Vaultsh 0.6.0 supports encrypted local vaults, limited offline Bitcoin wallet creation/recovery, read-only Bitcoin address balance/first-page history, and read-only native-asset balance queries on Ethereum, Polygon PoS, Arbitrum One, Optimism, and Base mainnets. EVM private-key derivation/storage, ERC-20 tokens, Monero, Tor transport, transaction construction, signing, and broadcasting are not implemented.

Network requests require a config permission and `--allow-network`. Endpoints are user-selected and the endpoint operator can learn queried addresses and connection metadata. Tor is not implemented; enabling `tor_enabled` causes current query commands to refuse a direct connection.

## Security limitations

- No independent security or cryptographic audit has been performed.
- Test results do not constitute a security certification.
- Python memory handling does not promise secret zeroization.
- Recovery phrases are displayed in a terminal and may be captured by screen recording or screenshots.
- Provider-supplied balance/history data is not independently verified as a cryptographic proof.

See [the security model](docs/SECURITY_MODEL.md) and [the encrypted vault format](docs/VAULT_FORMAT.md) before changing storage or network code.
