# Security model

This document describes the current boundaries of Vaultsh **0.6.0**. Vaultsh is pre-alpha, unaudited, and unsuitable for real funds.

## Assets

- Recovery phrases stored inside the encrypted vault payload.
- The vault password and encrypted vault/backup files.
- Addresses and endpoint metadata associated with network queries.
- Integrity of locally displayed public wallet information and provider-supplied balances.

## Assumptions

Vaultsh assumes Python and its dependencies are installed from trusted sources, the operating system and local user account are not compromised, and the user reviews any endpoint before authorizing a network query. Those assumptions may not hold on a malware-infected machine, shared computer, or untrusted package mirror.

## Protection mechanisms implemented

- Vault document contents use Scrypt-derived key material and AES-256-GCM authenticated encryption.
- Random salts/nonces come from the operating system.
- Vault data is validated after decryption; writes use the project's atomic-write helper.
- Normal wallet listing returns public summaries without mnemonics.
- Showing a recovery phrase requires explicit confirmation and unlocking the vault.
- Network operations need both configuration permission and `--allow-network`.
- Endpoints are user-selected; remote URLs require HTTPS; credentials/query/fragment and path traversal are rejected.
- Network responses are bounded by byte limits and timeouts. Redirects are disabled and ambient proxy variables are ignored.
- EVM RPC validates the JSON-RPC version/request ID and requires the chain ID to match one of five explicit network profiles. Mixed-case EVM addresses require EIP-55 checksum validation.
- Bitcoin history validates transaction IDs/status fields and caps the number of displayed rows.

## Known weaknesses and gaps

- No independent cryptographic, key-management, or application security audit has occurred.
- Python does not guarantee zeroization of secrets from memory.
- Recovery words are displayed in the terminal at creation; terminal capture/screen recording can expose them.
- Anyone with the recovery phrase can recover the corresponding Bitcoin wallet regardless of the vault password.
- The current vault record schema stores Bitcoin wallet records only. EVM support is read-only and stores no EVM private keys.
- Bitcoin address balance/history results are limited to one address and a provider's current response; the app does not scan all wallet addresses or independently verify state proofs.
- EVM balance data is supplied by the chosen RPC provider. It is not a balance proof. The endpoint learns the queried address and connection metadata.
- Endpoint validation cannot make a provider trustworthy, prevent network-level observation, or defend a compromised endpoint. Users must configure only endpoints they trust.
- Tor transport, transaction construction, fee/gas handling, signing, broadcasting, wallet-wide history, EVM transaction history, token balances, and Monero are not implemented.
- Tests use mock responses. Tests do not certify real-world interoperability, operation on every platform, or security.

## Network privacy flow

For a network query, the CLI validates config, requires explicit command-line intent, refuses to connect if `tor_enabled` is true because Tor transport is not implemented, constructs the selected client, then sends only the documented read-only query. No automatic fallback to direct connection occurs from a Tor setting. Public blockchain data remains publicly observable regardless of transport.

## Required work before real-funds use

1. Independent review of encryption, KDF parameters, vault format and file writes.
2. Independent review of Bitcoin key derivation and recovery against official vectors.
3. Secret lifecycle review including terminal output, exceptions, memory, backups, and compromised-machine scenarios.
4. Dependency/license/supply-chain review and reproducible release artifacts.
5. Fuzzing and adversarial testing of JSON schema, vault envelopes, endpoint URLs, Esplora payloads, and JSON-RPC payloads.
6. Platform CI and integration testing against controlled self-hosted nodes.
7. Security design review before implementing transaction construction, signing, broadcasting, or Tor transport.
8. Clear, private vulnerability-reporting process and an independent audit.

See [SECURITY.md](../SECURITY.md) for reporting guidance. Do not publish secrets or exploit details in a public issue.
