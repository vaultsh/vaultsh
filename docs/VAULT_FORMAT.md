# Encrypted vault format

This page describes the current vault implementation in Vaultsh **0.6.0**. The format is experimental and has not received an independent cryptographic or interoperability audit.

## File layers

A vault file has two layers:

1. An encrypted envelope produced by `vaultsh.crypto.encryption`.
2. A UTF-8 JSON document validated by `vaultsh.storage.vault_document`.

The outer envelope exposes format identification, KDF parameters, salt, and nonce. The document's metadata and Bitcoin recovery phrases are encrypted. Vaults and backups should be treated as sensitive files.

## Encryption envelope

The current envelope uses:

- Magic marker: `VSHV`.
- Envelope version: `1`.
- Password-based key derivation: Scrypt.
- Default Scrypt parameters: `N = 2**15`, `r = 8`, `p = 1`.
- Salt: 16 random bytes from the operating system.
- AES-GCM nonce: 12 random bytes.
- Encryption: AES-256-GCM, a 32-byte derived key, and an authentication tag.
- Header bytes are authenticated as additional data.
- Accepted Scrypt parameters are bounded before expensive derivation: `N` between `2**14` and `2**16` and a power of two, `r` from 1 to 8, and `p` from 1 to 4.
- The vault file layer caps input size at 64 MiB.

Wrong passwords and tampered ciphertext are reported as generic authentication/decryption failures. Do not invent custom cryptographic primitives or change parameters without tests and independent review.

## Inner document

The current schema is version 2. A representative metadata-only document before encryption is:

```json
{
  "schema": "vaultsh.vault",
  "schema_version": 2,
  "vault_id": "00000000-0000-4000-8000-000000000000",
  "label": "Main vault",
  "created_at": "2026-10-27T12:00:00+00:00",
  "wallets": []
}
```

The values are examples only.

### Shared fields

- `schema`: must equal `vaultsh.vault`.
- `schema_version`: an integer in the supported schema list.
- `vault_id`: canonical lowercase UUID.
- `label`: trimmed, non-empty string, maximum 80 characters, no control characters.
- `created_at`: ISO 8601 timestamp with timezone.
- `wallets`: a JSON list.

Unknown/missing fields are rejected. JSON booleans are not accepted where integers are required.

### Schema v1

Schema v1 is metadata-only with an empty wallet list. It remains readable by the current document reader but cannot contain wallet records.

### Schema v2

Schema v2 supports Bitcoin Mainnet wallet records only. Each record contains:

- `wallet_id`: canonical lowercase UUID.
- `label`: validated display label.
- `network`: `bitcoin-mainnet`.
- `address`: the implemented first Mainnet Native SegWit P2WPKH address.
- `derivation_path`: `m/84'/0'/0'/0/0`.
- `created_at`: ISO 8601 timestamp with timezone.
- `mnemonic`: normalized English BIP-39 recovery phrase with 12 or 24 words.

Duplicate IDs and duplicate addresses are rejected. The current schema does not support EVM or Monero wallet records, other Bitcoin derivation paths, other BIP-39 languages, or non-empty BIP-39 passphrases.

## EVM networks do not use this schema yet

Version 0.6.0 only performs read-only EVM JSON-RPC balance queries for its five explicit mainnet profiles. It neither generates EVM keys nor stores EVM wallet records. A schema migration is required before any EVM wallet secrets can be added safely.

## Migration

Opening or checking a v1 vault does not migrate it. Adding a Bitcoin wallet prepares and validates a new document, upgrades it to schema v2, encrypts it, and performs an atomic replacement. Make a backup before testing migrations. There is no general-purpose downgrade/export migration command.

## Wallet-secret handling

Bitcoin recovery phrases exist inside the JSON document only within the authenticated encrypted payload at rest. Normal `list_wallets()` summaries omit mnemonics. `wallet recovery-phrase` separately asks for confirmation and the vault password before displaying the phrase.

This does not protect against malware, compromised terminals, screenshots, process-memory inspection, or an attacker who has the recovery phrase. Python does not guarantee secret zeroization.

## Backups

Backups are byte-for-byte copies of the encrypted vault. Backup creation does not decrypt the source or verify the password. After restoring, run `vaultsh vault check` with the password. Keep a copy offline and protect it separately from the recovery phrase.

## Compatibility policy

There is no stable compatibility promise while pre-alpha. Any future schema/envelope change must include a written migration strategy, old/new/malformed-format tests, checks for secret leakage, changelog/docs updates, and independent review before real-funds use.
