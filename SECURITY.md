Security Policy
Vaultsh is an early-stage, pre-alpha project. It is not a production wallet and must not be used to protect or transact real funds. The modules in this repository are not a substitute for an audited wallet implementation.
Supported security scope
At this stage, the project provides application scaffolding, configuration validation, privacy-policy helpers, and a small encrypted-byte container based on the cryptography library. It does not implement seed generation/import, blockchain-specific private-key derivation, signing, balance retrieval, or transaction broadcasting.
Reporting a vulnerability
Please report suspected vulnerabilities privately to the repository maintainers using the security contact configured on the hosting platform (for example, GitHub's Report a vulnerability feature). If no private reporting channel is configured, first ask the maintainers to establish one rather than publishing exploit details immediately.

When reporting, include the affected version or commit, operating system, Python version, reproduction steps, and expected versus observed behavior. Never include seed phrases, private keys, passwords, decrypted vaults, personal wallet data, or other secrets. Use synthetic test data.
Security practices
- Never commit secrets, seed phrases, private keys, vault files, or backups.
- Do not send secrets to RPC providers, telemetry endpoints, issue trackers, or logs.
- Network requests and telemetry are disabled by default; network features must require explicit user intent and configuration.
- Use reviewed cryptographic primitives from maintained libraries. Do not invent algorithms or use fast general-purpose hashes as password KDFs.
- Treat encrypted-file parsing as untrusted input and bound KDF parameters and file sizes to reduce denial-of-service risk.
- Review destination, amount, network, and fee before any future transaction-signing operation.
- Make backup/restore behavior explicit and test it with disposable files.
- Run unit tests, linting, type checks, dependency audits, and platform checks before release.
- Obtain independent security review before describing Vaultsh as suitable for real funds.
Responsible disclosure
Please allow maintainers reasonable time to investigate and prepare a fix before publicly disclosing a vulnerability. Do not access, modify, or exfiltrate third-party data while investigating.
Current limitations
Encryption helpers alone do not make a wallet secure. Application-level secret handling, password policy, memory behavior, vault lifecycle, OS permissions, recovery, dependency security, chain integrations, and the complete threat model still require further design and review. Tor support is optional scaffolding only; Vaultsh does not currently route traffic through Tor or guarantee anonymity.