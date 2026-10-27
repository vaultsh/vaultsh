# Security model and limitations

## Status first

**Vaultsh 0.4.5 is experimental, pre-alpha, unaudited, and not suitable for real funds.** Passing automated tests proves only that tested cases passed; it does not establish the safety of the wallet or storage format.

## Assets to protect

- Recovery phrases and private key material derived from them.
- Vault passwords.
- Encrypted vault files and backups.
- Public wallet metadata that may reveal wallet ownership or intended use.
- Public addresses submitted to a balance endpoint and associated connection metadata.
- Future node/RPC connection metadata and configuration credentials.

A recovery phrase is a bearer secret: anyone who has it may recover the associated wallet without the Vaultsh password. The password protects the local vault file; it does not revoke or replace the recovery phrase.

## Implemented protections

- Recovery phrase entry uses hidden terminal prompts during recovery; vault password prompts are hidden.
- New vault passwords have a minimum length of 12 characters. Use a longer, unique, high-entropy password rather than relying on the minimum.
- Data is encrypted with AES-256-GCM using a Scrypt-derived key. Salt and nonce are generated from operating-system randomness; header fields are authenticated as associated data.
- Scrypt parameters from file input are validated against bounds before running the KDF.
- The encrypted vault file has a size limit.
- Writes use a temporary file and attempt an atomic write workflow; on supported non-Windows filesystems the implementation attempts to set permissions to `0600`.
- Existing files are not overwritten unless the relevant CLI option/helper explicitly permits it.
- Wallet records are validated and duplicate IDs/addresses are rejected.
- Standard wallet listing returns public metadata without recovery phrases.
- Revealing a phrase requires explicit confirmation and the vault password.
- Telemetry and network access are disabled by default. The balance command requires both configuration enablement and `--allow-network`.
- The balance client requires HTTPS for remote endpoints, permits HTTP only for loopback, rejects URL credentials/query/fragments, disables redirects and ambient environment proxies, bounds response size, and uses a timeout.
- The balance client accepts a public address only; it does not receive wallet secrets.
- If `tor_enabled = true`, the balance command refuses to connect, avoiding a direct-connection fallback that might be mistaken for Tor protection.

These are implemented safeguards, not a security guarantee. File permissions differ across operating systems, and atomic-write behavior depends on filesystem semantics.

## Threats not solved

Vaultsh does not protect against:

- Malware, remote access, keyloggers, process-memory inspection, a compromised Python environment, a hostile administrator, or physical access to an unlocked machine.
- Secrets captured by terminals, screen sharing, screenshots, streaming, clipboard managers, shell instrumentation, or logs.
- Weak vault passwords and offline guessing against stolen vaults/backups.
- Loss, theft, or disclosure of the recovery phrase.
- Address reuse, blockchain analysis, endpoint metadata collection, or identification of public-chain transactions.
- Incorrect, stale, incomplete, or malicious balance data supplied by the selected API.
- Errors in `embit`, Python, the operating system, cryptographic dependencies, the API provider, or this application's integration.

Python strings and intermediate objects cannot be reliably zeroized with the guarantees expected from some lower-level secure-memory designs.

## Network and privacy model

Wallet phrase generation, recovery, and first-address derivation operate locally. The optional balance command performs one read-only request to the exact user-supplied endpoint, with `GET /address/{address}`. It requires both `network_requests_enabled = true` in the chosen TOML file and `--allow-network` on the command line. No endpoint is selected automatically.

The endpoint receives the requested public address and can observe connection metadata, potentially including the client's IP address and request timing. A trusted self-hosted service can reduce third-party exposure but does not eliminate network metadata or host risks. Returned balance data is not independently verified by Vaultsh and is not a proof of wallet ownership.

The client requires HTTPS for remote hosts, permits plain HTTP only on localhost/loopback, does not follow redirects, and ignores ambient proxy environment variables. This is a direct request; Tor is not implemented. If the config enables `tor_enabled`, the CLI refuses to connect. Public blockchain activity remains observable and may be traceable regardless of transport.

## Recovery and backup recommendations

- Write the phrase down offline and verify it independently before relying on a wallet.
- Keep recovery material separate from the encrypted vault and its backup.
- Store a backup in a second protected location and periodically verify that it can be opened.
- Never upload vaults, backups, phrases, or passwords to public issue trackers or share them in chat.
- Do not accept a phrase through shell arguments or environment variables; command-line history and process listings can expose arguments.
- Use only synthetic data for tests and bug reports.

## Before considering a real-funds release

A release candidate needs, at minimum:

1. Independent review of the encryption envelope, KDF parameters, file format, and atomic-write behavior on supported filesystems.
2. Independent review of BIP-39/BIP-32/BIP-84 integration against authoritative vectors.
3. Secret-lifecycle analysis covering prompts, exceptions, logging, terminal output, process memory, and backups.
4. Dependency and supply-chain review, reproducible release artifacts, and platform CI.
5. Fuzzing and malformed-input tests for encrypted envelopes, JSON schemas, and user-supplied phrases.
6. Network-client privacy and interoperability review, plus address-discovery tests before wallet-wide balances are reported.
7. Security design review of transaction construction, signing, and broadcast before any implementation.
8. A documented responsible-disclosure process and independent security audit.

## Vulnerability reporting

Follow [SECURITY.md](../SECURITY.md). Do not include live wallet secrets or real funds in a report. Use a private repository security channel where one is configured; do not publish exploit details prematurely.
