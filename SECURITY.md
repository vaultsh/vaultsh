# Security Policy

Vaultsh is an early-stage, pre-alpha project. It is **not an audited or production-ready wallet** and must not be used to protect or transact real funds. Version 0.4.5 adds only a read-only Bitcoin address-balance lookup; it does not add transaction signing or broadcast.

For the full threat model, secret-handling guidance, and release requirements, see [docs/SECURITY_MODEL.md](docs/SECURITY_MODEL.md). For implementation boundaries and testing, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

## Supported security scope

Version 0.4.5 can:

- Generate a 12-word English BIP-39 recovery phrase from operating-system entropy.
- Derive the first Bitcoin Mainnet native-SegWit (BIP-84) receiving address.
- Store recovery phrases and public metadata inside an authenticated encrypted local vault.
- Import valid 12- or 24-word English BIP-39 phrases into that vault (empty BIP-39 passphrase only).
- Fetch read-only confirmed and net-unconfirmed transaction-output statistics for one user-supplied Bitcoin Mainnet address using a user-selected Esplora-compatible API, when both config and CLI opt-in are enabled.

It does **not** discover all wallet addresses, aggregate a wallet-wide balance, fetch full transaction history, construct or sign transactions, or broadcast payments. It does not support the BIP-39 optional passphrase, Ethereum/EVM, or Monero. Tor transport is not implemented.

## Reporting a vulnerability

Please report suspected vulnerabilities privately to the repository maintainers using the security contact configured on the hosting platform (for example, GitHub's **Report a vulnerability** feature). If no private reporting channel is configured, first ask maintainers to establish one rather than publishing exploit details immediately.

When reporting, include the affected version or commit, operating system, Python version, reproduction steps, and expected versus observed behavior. **Never include seed phrases, private keys, passwords, decrypted vaults, personal wallet data, API credentials, or other secrets.** Use synthetic test data. For network issues, redact addresses and endpoints if sharing them could identify private activity.

## Security practices and user responsibilities

- Never commit or send recovery phrases, private keys, passwords, vault files, or backups to issue trackers, chat, cloud notes, or support channels.
- The recovery phrase controls the wallet. Anyone who obtains it can derive its private keys, even without the Vaultsh vault password.
- Keep the recovery phrase in a separate, offline location from the encrypted vault file. Test recovery before trusting wallet software.
- Use a unique, high-entropy vault password. Encrypted backups permit offline password guessing if a password is weak.
- Do not store passwords or recovery phrases in TOML configuration.
- Network requests and telemetry are disabled by default. The balance command additionally requires `--allow-network` and a trusted endpoint specified by the user.
- A balance query discloses the address and connection metadata to the selected endpoint. Remote endpoints must use HTTPS. A provider may return stale, incomplete, incorrect, or malicious data.
- The balance client does not follow redirects, does not use ambient environment proxy variables, and does not route through Tor. If `tor_enabled = true`, the command refuses the query rather than connecting directly.
- Use established cryptographic primitives and standards rather than inventing new cryptographic algorithms.
- Treat encrypted files and API responses as untrusted input. Keep parsers bounded and validate input sizes and schema.
- Run unit tests, linting, type checks, dependency audits, and platform checks before release.
- Obtain independent review of cryptography, wallet derivation, storage format, network integration, and secret handling before any real-funds use.

## Known limitations

The wallet workflow has not received independent security review. Python does not guarantee reliable zeroization of secret strings or intermediate key material from memory. The current workflow stores the recovery phrase in the encrypted vault and prints it on creation; terminal capture, screen sharing, clipboard managers, and process instrumentation can expose it. The phrase-display command requires explicit confirmation but cannot prevent OS-level capture.

The wallet derives only its first BIP-84 receive address. The balance command queries only the address given on the command line and cannot prove ownership or aggregate the whole wallet. Public blockchain activity can be traceable. Tor settings do not route traffic through Tor or guarantee anonymity.

## Responsible disclosure

Please allow maintainers reasonable time to investigate and prepare a fix before publicly disclosing a vulnerability. Do not access, modify, or exfiltrate third-party data while investigating.

## Version scope notes

- **0.4.5:** Adds explicitly authorized read-only Esplora address statistics. Network calls require the supplied config to enable requests and the explicit `--allow-network` flag; Tor-enabled configuration causes the query to be refused.
- **0.3.0:** Added encrypted Bitcoin wallet records in schema v2. Schema-v1 metadata-only vaults remain readable and are upgraded when a wallet is added.
- **0.2.0 and earlier:** Vaults stored metadata only and did not support wallet secrets.

All releases remain experimental. Use synthetic test data only; do not store or transact real funds.
