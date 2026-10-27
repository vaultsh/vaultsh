# Architecture

## Design goals

Vaultsh is a Python-first, terminal-oriented wallet foundation with local-first defaults. It keeps user interaction, wallet-domain models, chain-specific rules, encrypted storage, and optional network transports separated. Vaultsh 0.4.5 remains a small pre-alpha implementation rather than a fully layered production wallet.

## High-level flow

```text
User / Terminal
      |
      v
Typer CLI (cli.py) -----> Rich UI helpers
      |
      +----> Config + network policy (explicit opt-in gate)
      |
      +----> Vault / wallet-store operations
      |             |
      |             +----> Bitcoin adapter (BIP-39 / BIP-84, offline)
      |
      +----> Bitcoin Esplora client (read-only address statistics)
      |
      v
Versioned vault document <----> Encrypted file I/O <----> Encryption envelope
```

The Esplora path is separate from wallet creation and vault storage. It accepts a public address, not a seed phrase or vault file, and cannot sign or submit transactions.

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
│   └── derivation.py           # Derivation-path parser, not key derivation
├── networks/
│   ├── base.py                 # Minimal network-adapter Protocol and errors
│   └── bitcoin/
│       ├── wallet.py           # Offline BIP-39/BIP-84 operations
│       └── client.py           # Read-only, explicit Esplora API client
├── privacy/
│   ├── network_policy.py       # Explicit request + config permission gate
│   └── tor.py                  # SOCKS settings only; not a transport
├── storage/
│   ├── vault.py                # Encrypted file I/O and atomic replacement
│   ├── vault_document.py       # Versioned inner JSON schema
│   ├── wallet_store.py         # Encrypted wallet-record operations
│   └── backup.py               # Encrypted file copy/restore
└── ui/
    ├── panels.py               # Rich notice panels
    └── prompts.py              # Sensitive-action prompts / transaction text helper
```

The repository also contains `tests/`, root documentation, `pyproject.toml`, and the GPL license.

## Module responsibilities

### CLI and UI

`cli.py` defines user-facing commands, obtains passwords and phrases through hidden prompts, calls domain/storage functions, checks network policy, and formats output. It should not implement cryptographic algorithms. UI helpers are presentation-only and should not read vaults or derive keys.

### Core and chain adapters

`core/wallet.py` models public wallet summary information. `networks/base.py` defines a minimal protocol for future chain adapters. `networks/bitcoin/wallet.py` owns Bitcoin-specific BIP-39/BIP-84 derivation and delegates standards-based key derivation to `embit`.

`networks/bitcoin/client.py` calls a user-specified Esplora-compatible `GET /address/{address}` endpoint. It validates the endpoint before making a request, requires callers to enforce the network policy, uses a bounded response body and timeout, disables redirects and environment proxy use, parses confirmed/mempool transaction-output sums, and exposes balances in integer satoshis. It never receives a mnemonic or a vault password.

Do not put Bitcoin address encodings or path rules into a generic helper and assume Ethereum or Monero use the same rules. Each chain adapter must implement and test its own address, key, transaction, and network rules.

### Cryptography and storage

`crypto/encryption.py` implements a password-derived encryption envelope. `storage/vault.py` reads/writes authenticated encrypted bytes and attempts atomic writes. `storage/vault_document.py` validates the JSON document stored inside the encrypted payload. `storage/wallet_store.py` adds and lists wallet records and retrieves phrases for the explicit reveal command. `storage/backup.py` copies encrypted bytes without decrypting them.

These boundaries are helpful but do not constitute a formal security proof. The data format and full secret lifecycle require independent review before any real-funds use.

### Privacy and network permission

`config.py` validates application preferences. `privacy/network_policy.py` requires both explicit user intent and configuration permission. The balance command requires the supplied TOML file to enable `network_requests_enabled` and the command to include `--allow-network`. There is no default endpoint.

Remote endpoints must use HTTPS. Plain HTTP is accepted only for localhost or loopback IP addresses. The Esplora client disables automatic redirects and ambient proxy settings so the target is not silently changed; the request is direct and does not use Tor. If `tor_enabled = true`, the CLI refuses the request rather than presenting a direct request as Tor-protected.

### User interface

Rich tables and panels present command results. Public address/balance output is distinct from secret recovery-phrase output. A balance result includes a privacy notice because a remote endpoint may associate an address with connection metadata.

## Dependency direction

Prefer this direction:

- `cli.py` may call `config`, `networks`, `storage`, `privacy`, and `ui`.
- `storage` may call `crypto`, `core` models, and required chain-specific validation.
- A chain adapter may use standards libraries but must not depend on terminal rendering.
- `ui` should be presentation-only.
- `crypto` should not import Typer, Rich, or CLI code.
- The network client should never receive seed phrases, vault passwords, private keys, or decrypted vault documents.

Avoid circular imports and avoid secrets in public summary models, logs, or exception messages.

## Future architectural work

The next stages include platform CI, dependency/security scanning, network-client interoperability tests, address discovery with a gap limit, and wallet-wide accounting. Transaction construction, PSBT handling, signing, and broadcasting need separate designs and reviews; they must not be introduced merely because a read-only query works.
