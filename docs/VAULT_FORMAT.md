# Encrypted vault format

This page documents the current local file format as implemented in Vaultsh 0.4.5. It is useful for maintainers and test authors, not an endorsement of the format for production use. The format has not received an independent cryptographic or interoperability audit and may change while the project is pre-alpha.

## File layers

A vault file has two logical layers:

1. An encrypted envelope produced by `vaultsh.crypto.encryption`.
2. A UTF-8 JSON document inside the envelope, validated by `vaultsh.storage.vault_document`.

The outer envelope exposes format identification and bounded KDF parameters, salt, and nonce; the document fields and wallet recovery phrases are encrypted. Encrypted bytes and their backups are sensitive artifacts.

## Encryption envelope

The current envelope uses:

- Magic marker: `VSHV`.
- Envelope version: `1`.
- Password-based key derivation: Scrypt.
- Default Scrypt parameters: `N = 2**15`, `r = 8`, `p = 1`.
- Salt: 16 random bytes from the operating system.
- AES-GCM nonce: 12 random bytes.
- Encryption: AES-256-GCM, 32-byte derived key, authenticated ciphertext/tag.
- Header bytes are supplied as AES-GCM associated data, so tampering with the envelope header causes authentication failure.
- Accepted Scrypt parameters are bounded before expensive derivation: `N` between `2**14` and `2**16` and a power of two, `r` from 1 to 8, and `p` from 1 to 4.
- Vault file size is capped at 64 MiB by the file layer.

A wrong password and a modified ciphertext return a generic decryption/authentication error at the envelope layer. The envelope format has not been independently reviewed; changes must preserve authenticated encryption and must not invent custom cryptographic primitives.

## Inner document

The current document has these top-level fields:

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

Values above illustrate the shape only; the UUID and timestamp are examples.

### Shared fields

- `schema`: must be `vaultsh.vault`.
- `schema_version`: must be an integer version the application supports.
- `vault_id`: canonical lowercase UUID.
- `label`: non-empty, trimmed string with a maximum of 80 characters and no control characters.
- `created_at`: ISO 8601 timestamp including timezone information.
- `wallets`: a JSON list.

Unknown or missing top-level fields are rejected. Schema version must be a JSON integer, not a boolean.

### Schema v1

Version 1 is a metadata-only format with an empty `wallets` list. A schema-v1 vault can be opened and checked by the current reader. It cannot contain wallet records.

### Schema v2

Version 2 supports Bitcoin Mainnet wallet records. Each record contains exactly:

- `wallet_id`: canonical lowercase UUID.
- `label`: validated display label.
- `network`: `bitcoin-mainnet`.
- `address`: first Mainnet native-SegWit P2WPKH address in the supported `bc1q...` format.
- `derivation_path`: currently fixed to `m/84'/0'/0'/0/0`.
- `created_at`: ISO 8601 timestamp including timezone.
- `mnemonic`: normalized lowercase English BIP-39 words, 12 or 24 words.

Duplicate wallet IDs and duplicate addresses are rejected. This initial schema does not support arbitrary account paths, other networks, BIP-39 languages, or non-empty BIP-39 passphrases.

## Schema migration

Opening or checking a v1 vault does not migrate it. When a wallet is added, the storage layer prepares and validates the new document, changes `schema_version` to 2, encrypts it, and atomically replaces the file. If the write fails, the prior file should remain intact according to the intended atomic-write path; filesystem and platform behavior still deserve additional cross-platform testing.

Always create a backup before experimenting with new builds or storage migrations. The current implementation has no general-purpose downgrade/export migration command.

## Wallet secret storage

Recovery phrases are in the JSON document but only inside the authenticated encrypted payload at rest. `list_wallets()` returns public `WalletSummary` data and does not return a mnemonic. The explicit `wallet recovery-phrase` command separately asks the user to confirm and unlock the vault before displaying it.

This does not protect against an attacker who can read the phrase while it is displayed, inspect a compromised process, obtain the password and vault, or compromise the machine. Python does not guarantee secret zeroization.

## Backups

Backups are byte-for-byte copies of the encrypted source file. The copy helper checks file size and the `VSHV` marker, but it does not decrypt the source or prove that the password is correct. Run `vaultsh vault check` against the restored copy to authenticate and validate it.

## Compatibility policy

There is no stable backward-compatibility promise in pre-alpha. Any change to the envelope or document schema must include:

1. A written format change and migration/downgrade policy.
2. Tests for old and new formats plus malformed inputs.
3. Tests ensuring secret fields never leak in public summaries or raw plaintext exports.
4. Changelog and security documentation updates.
5. Independent review before the format is used with real funds.
