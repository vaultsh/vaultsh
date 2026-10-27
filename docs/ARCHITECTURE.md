# Architecture — Vaultsh 1.0.0-beta.1

Vaultsh is a Python CLI/TUI with explicit separation between UI, encrypted storage, chain-specific key/transaction logic and networking. Beta status is not a security certification.

## Layers

- `cli.py`: Typer commands, validation prompts, review panel and typed confirmation.
- `ui/tui.py`, `ui/screens.py`, `ui/i18n.py`: Textual UI, Rich fallback, EN/PL/RU strings. The TUI exposes basic vault/wallet and read-only-query forms; send workflows are CLI commands.
- `core/`: common app-level models and rules.
- `crypto/`: authenticated encryption and derivation path helpers.
- `storage/`: vault documents, atomic encrypted file operations, backups and wallet records.
- `networks/bitcoin/`: BIP-84 wallet derivation, Esplora query client, limited UTXO selection, PSBT/finalization/signing and broadcast.
- `networks/ethereum/`: native ETH JSON-RPC and local legacy EIP-155 transaction signing.
- `networks/solana/`: Mainnet RPC, native SOL transfer and signing with `solders`.
- `networks/monero/`: strict loopback client for official `monero-wallet-rpc`; the RPC owns the Monero wallet files and signing.
- `privacy/network_policy.py`: config permission plus explicit CLI authorization; Tor-enabled requests fail closed because Tor transport is not implemented.

## Security-sensitive flow

For BTC/ETH/SOL, the app loads a wallet record from the password-unlocked encrypted vault, queries the explicitly selected endpoint, builds and signs a chain-specific transaction locally, shows destination/amount/fee/network and asks for a phrase matching the transaction details before broadcast. No `--yes` broadcast bypass exists. For XMR, `monero-wallet-rpc` prepares an unrelayed transaction; Vaultsh shows the preview, gets typed confirmation, then calls `relay_tx` using the metadata returned by the prepare step.

Every endpoint query/send needs `[app].network_requests_enabled = true` and `--allow-network`. Endpoint URL is explicit; this does not conceal addresses or IP metadata.

## Important limitation

Bitcoin input discovery currently checks only confirmed UTXOs for the first receiving address. Change goes to `m/84'/0'/0'/1/0`, not scanned by Vaultsh yet. Other wallets using the same recovery phrase and standard can discover it, but Vaultsh cannot currently manage change outputs. Do not send real BTC with this beta.

## Dependency boundaries

`embit` handles Bitcoin BIP-39/BIP-32 and transaction structures; `eth-account` signs ETH transactions; `bip-utils` derives Solana keys; `solders` builds/signs Solana transactions; `qrcode` renders public-address QR images; official Monero wallet RPC handles XMR wallet keys and transactions. There is no generic cross-chain signing method.
