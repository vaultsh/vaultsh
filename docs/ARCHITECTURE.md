# Architecture

## Design goals

Vaultsh is a Python-first, terminal-oriented wallet foundation with local-first defaults. It aims to keep user interaction, wallet-domain models, chain-specific rules, encrypted storage, and optional network transports separated. The current release is a small pre-alpha implementation rather than a fully layered production wallet.

The intended high-level flow is:

```text
User / Terminal
      |
      v
Typer CLI (cli.py) -----> Rich UI helpers
      |
      v
Application operations
      |                  \
      v                   v
Wallet store             Configuration / privacy policy
      |
      +----> Bitcoin adapter (BIP-39 / BIP-84, offline)
      |
      v
Vault document <----> Vault file operations <----> Encryption envelope
```

## Source tree

```text
src/vaultsh/
├── __init__.py                 # Package version
├── __main__.py                 # `python -m vaultsh` entry point
├── cli.py                      # Typer commands and orchestration
├── config.py                   # Validated non-secret TOML settings
├── core/
│   └── wallet.py               # Public wallet summary model
├── crypto/
│   ├── encryption.py           # Scrypt + AES-256-GCM envelope
│   └── derivation.py           # BIP32-style path parser only
├── networks/
│   ├── base.py                 # Minimal network-adapter Protocol
│   └── bitcoin/
│       └── wallet.py           # Offline BIP-39/BIP-84 operations
├── privacy/
│   ├── network_policy.py       # Explicit permission gate for future clients
│   └── tor.py                  # SOCKS proxy settings, not a Tor transport
├── storage/
│   ├── vault.py                # Encrypted file I/O and atomic replacement
│   ├── vault_document.py       # Versioned inner JSON schema v1/v2
│   ├── wallet_store.py         # Encrypted wallet-record operations
│   └── backup.py               # Encrypted file copy/restore
└── ui/
    ├── panels.py               # Rich notice panels
    └── prompts.py              # Sensitive action prompts / transaction text helper
```

The repository also contains `tests/`, root documentation, `pyproject.toml`, and the GPL license.

## Module responsibilities

### CLI and UI

`cli.py` defines user-facing commands, obtains passwords/phrases through prompts, invokes domain/storage functions, and formats output. It should not implement cryptographic algorithms. `ui/` contains reusable presentation helpers; it should not read vaults or derive keys.

### Core and chain adapters

`core/wallet.py` models public wallet summary information. `networks/base.py` defines a minimal protocol for future network adapters. `networks/bitcoin/wallet.py` owns the currently supported Bitcoin-specific BIP-39/BIP-84 behavior and delegates standards-based derivation to `embit`.

Do not put Bitcoin address encodings or path rules into a generic helper and assume Ethereum or Monero will use them. Each chain adapter must implement and test its own address, key, transaction, and network rules.

### Cryptography and storage

`crypto/encryption.py` implements a password-derived encryption envelope. `storage/vault.py` reads and writes authenticated encrypted bytes, enforces a maximum file size, and attempts atomic writes. `storage/vault_document.py` validates the JSON document stored inside the encrypted payload. `storage/wallet_store.py` adds and lists wallet records and retrieves a phrase for the explicit reveal command. `storage/backup.py` copies encrypted bytes without decrypting them.

These boundaries are helpful but do not constitute a formal security proof. The data format and full secret lifecycle still require independent review before any real-funds use.

### Privacy configuration

`config.py` validates application preferences. `privacy/network_policy.py` provides a helper that requires both explicit intent and configuration approval before a future client may connect. `privacy/tor.py` builds SOCKS5 settings using remote DNS (`socks5h://`). No current feature uses this helper to make live network requests, and Vaultsh does not start or manage a Tor process.

## Data flows

### Creating a wallet

1. The CLI checks that the target vault exists and prompts for the vault password without echoing it.
2. The Bitcoin adapter obtains 128 bits from the operating system CSPRNG and produces an English 12-word BIP-39 phrase using `embit`.
3. The adapter derives the BIP-84 first receiving address at `m/84'/0'/0'/0/0`.
4. The wallet store decrypts and validates the existing vault document, checks for a duplicate address, adds the record, upgrades schema v1 to v2 if needed, then encrypts and atomically replaces the file.
5. The CLI displays the address and phrase. The phrase is a high-value secret and must be recorded offline.

### Listing wallets

The store decrypts and validates the vault but returns `WalletSummary` objects without mnemonic fields. The CLI prints public metadata only. This is a code-path boundary, not protection against malware or a compromised process with access to the vault password.

### Backups

Backup and restore copy bytes without decrypting the payload. They check that the source resembles a Vaultsh encrypted file, but the copy operation does not authenticate the password or validate the inner document. Run `vaultsh vault check` against a restored copy to verify it with the password.

## Dependency direction

Prefer this direction:

- `cli.py` may call `config`, `networks`, `storage`, `privacy`, and `ui`.
- `storage` may call `crypto`, `core` models, and required chain-specific validation.
- a chain adapter may use standards libraries, but must not depend on terminal rendering.
- `ui` should be presentation-only.
- `crypto` should not import Typer, Rich, or CLI code.

Avoid circular imports and avoid placing secrets in public summary models, logs, or exception messages.

## Future architectural work

Before implementing RPC, address discovery, or transactions, add explicit service interfaces, chain-specific models, deterministic mocks, authoritative test vectors, bounded input parsing, and integration tests. Network transport must be opt-in and use the privacy policy. Signing and transaction broadcasting require separate review and should not be introduced merely because address derivation works.
