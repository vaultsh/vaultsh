# Architecture

This document describes the implemented boundaries in Vaultsh **0.6.0**. It is a maintenance guide, not a security audit or a stable public API promise.

## Source layout

```text
src/vaultsh/
├── __init__.py                 # Package version
├── __main__.py                 # python -m vaultsh entry point
├── cli.py                      # Typer commands, prompts, and Rich output
├── config.py                   # Validated non-secret TOML settings
├── core/wallet.py              # Network-neutral public wallet summary
├── crypto/                     # Vault encryption and path helpers
├── networks/
│   ├── base.py                 # Shared protocol and NetworkError
│   ├── bitcoin/
│   │   ├── wallet.py           # BIP-39/BIP-32/BIP-84 receiving address
│   │   └── client.py           # Esplora balance and address-history queries
│   └── ethereum/
│       └── client.py           # Read-only EVM JSON-RPC native-balance queries
├── privacy/                    # Network policy and Tor configuration helpers
├── storage/                    # Encrypted vault document, backup, wallet records
└── ui/                         # Reusable Rich panels and prompts
```

`tests/` mirrors key behaviors: CLI, configuration, Bitcoin client/wallet, Ethereum client, encrypted storage, privacy policy, and UI formatting.

## Responsibility boundaries

### CLI (`cli.py`)

The CLI binds user intent to domain operations. It reads non-secret configuration, checks the dual network opt-in, refuses network operations when Tor is configured but unavailable, and formats public output. It should not implement cryptographic primitives or parse arbitrary RPC responses inline.

### Configuration (`config.py`)

Configuration is for operational preferences only. It defaults telemetry and network requests off. No passwords, recovery phrases, private keys, API tokens, or derived keys belong here.

### Cryptography and storage

`crypto/encryption.py` implements the local encrypted envelope. `storage/vault_document.py` validates the inner versioned document. `storage/wallet_store.py` stores the current Bitcoin wallet records in the encrypted payload and returns public summaries without recovery phrases. `storage/backup.py` handles encrypted byte-for-byte copies.

EVM balance lookups are read-only and do not add EVM private keys or wallet records to the vault; the current inner schema supports Bitcoin wallet records only.

### Network adapters

Chain-specific code must own address formats, RPC schemas, units, derivation standards, and error validation:

- `networks/bitcoin/wallet.py` uses `embit` for English BIP-39 and the first BIP-84 Mainnet receive address.
- `networks/bitcoin/client.py` queries the one supplied address via Esplora for balance and first-page transactions.
- `networks/ethereum/client.py` holds an explicit allow-list of five EVM mainnet profiles, validates a 20-byte address and mixed-case EIP-55 checksum, verifies `eth_chainId` against the selected profile, and requests `eth_getBalance` in 18-decimal base units. It does not implement EVM key management or token contracts.

The shared `NetworkAdapter` protocol does not imply that all chains share derivation or signing rules. Monero must have a separate cryptographic design and has no implementation in this version.

### Privacy policy

The CLI enforces both explicit intent (`--allow-network`) and configuration (`network_requests_enabled = true`). Network adapters use explicitly selected endpoints, do not follow redirects, and ignore ambient proxy environment variables. They currently make direct requests. Setting `tor_enabled = true` causes the CLI to refuse these network operations rather than imply that traffic was routed through Tor.

## Dependency direction

Keep the preferred flow:

`cli -> config/privacy gate -> chain adapter or storage service -> crypto/storage primitives`

Avoid circular imports and avoid letting UI code make network requests. Network adapters should not choose public providers or silently fetch balances during wallet creation/listing.

## Future extension rules

Before adding a chain, define its mainnet identifiers, address validation, key derivation and recovery standards, transaction model, unit conversions, RPC semantics, privacy exposure, and official test vectors. Add tests before advertising a capability. An `__init__.py`, folder, or adapter protocol is not implementation evidence.
