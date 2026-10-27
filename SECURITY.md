# Security Policy

Vaultsh is an early-stage, pre-alpha project. It is **not an audited or production-ready wallet** and must not be used to protect or transact real funds. Current wallet support is intentionally limited to offline Bitcoin Mainnet phrase generation/recovery and first-address derivation.

For the full threat model, secret-handling guidance, and release requirements, see [docs/SECURITY_MODEL.md](docs/SECURITY_MODEL.md). For the implementation boundaries and test workflow, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

## Supported security scope

Version 0.3.0 can:

- Generate a 12-word English BIP-39 recovery phrase from operating-system entropy.
- Derive the first Bitcoin Mainnet native-SegWit (BIP-84) receiving address.
- Store the recovery phrase and public metadata inside an authenticated encrypted local vault.
- Import a valid 12- or 24-word English BIP-39 recovery phrase into that vault.

It **does not** connect to a blockchain or RPC service, scan balances or address history, construct or sign transactions, or broadcast payments. It does not support the optional BIP-39 passphrase, other Bitcoin address standards, Ethereum/EVM, or Monero yet.

## Reporting a vulnerability

Please report suspected vulnerabilities privately to the repository maintainers using the security contact configured on the hosting platform (for example, GitHub's **Report a vulnerability** feature). If no private reporting channel is configured, first ask the maintainers to establish one rather than publishing exploit details immediately.

When reporting, include the affected version or commit, operating system, Python version, reproduction steps, and expected versus observed behavior. **Never include seed phrases, private keys, passwords, decrypted vaults, personal wallet data, or other secrets.** Use synthetic test data.

## Security practices and user responsibilities

- Never commit or send recovery phrases, private keys, passwords, vault files, or backups to issue trackers, chat, cloud notes, or support channels.
- The recovery phrase controls the wallet. Anyone who obtains it can derive its private keys, even without the Vaultsh vault password.
- Keep the recovery phrase in a separate, offline location from the encrypted vault file. Test recovery before trusting any wallet software.
- Use a unique, high-entropy vault password. Encrypted backups permit offline password guessing if a password is weak.
- Do not store passwords or recovery phrases in the TOML configuration.
- Network requests and telemetry are disabled by default; wallet creation and address derivation should be offline.
- Use established cryptographic primitives and standards rather than inventing new cryptographic algorithms.
- Treat encrypted-file parsing as untrusted input and bound KDF parameters and file sizes to reduce denial-of-service risk.
- Run unit tests, linting, type checks, dependency audits, and platform checks before release.
- Obtain independent review of the cryptography, wallet implementation, file format, and complete secret-handling lifecycle before any real-funds use.

## Known limitations

The wallet workflow has not received independent security review. Python does not guarantee reliable zeroization of secret strings or intermediate key material from memory. The current workflow stores the recovery phrase in the encrypted vault and prints it on creation; terminal capture, screen sharing, clipboard managers, and process instrumentation can expose it. The phrase-display command requires explicit confirmation but cannot prevent OS-level capture.

The first-address-only implementation does not check whether that address is funded or whether the account has additional activity. No balance, fee, transaction preview, signature, or broadcast functionality is implemented. Public blockchain activity can be traceable; Tor scaffolding does not route traffic through Tor or guarantee anonymity.

## Responsible disclosure

Please allow maintainers reasonable time to investigate and prepare a fix before publicly disclosing a vulnerability. Do not access, modify, or exfiltrate third-party data while investigating.

## Version scope notes

- **0.3.0:** Schema v2 supports encrypted Bitcoin wallet records. Schema-v1 metadata-only vaults remain readable and are upgraded when a wallet is added.
- **0.2.0 and earlier:** Vaults stored metadata only and did not support wallet secrets.

All releases remain experimental. Use synthetic test data only; do not store or transact real funds.
