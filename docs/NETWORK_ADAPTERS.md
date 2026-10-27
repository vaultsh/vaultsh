# Network adapters — Vaultsh 1.0.0-beta.1

## Capability matrix

| Network | Read-only | Send | Important boundary |
|---|---|---|---|
| Bitcoin Mainnet | Address balance and first-page history via explicit Esplora | Local P2WPKH signing and Esplora broadcast | **Do not send real funds:** only confirmed UTXOs at first receive address are discovered; change branch `/1/0` is not scanned by Vaultsh yet |
| Ethereum Mainnet (chain ID 1) | Native ETH balance via JSON-RPC | Local legacy EIP-155 native ETH transfer | No EIP-1559, ERC-20, contract interactions or receipt/finality polling |
| Polygon PoS (137), Arbitrum One (42161), Optimism (10), Base (8453) | Native balances via JSON-RPC with `eth_chainId` profile pinning | Disabled | Balance queries only |
| Solana Mainnet Beta | Native SOL balance via JSON-RPC and Mainnet genesis-hash check | Locally signed native SOL transaction via `solders` | SPL tokens, address discovery, history and finality polling absent |
| Monero Mainnet | Local official wallet RPC address/balance | Official wallet RPC prepares an unrelayed XMR transfer, typed confirmation, then relay | Wallet files and seed stay under `monero-wallet-rpc`, separate from Vaultsh vault; keep RPC loopback-only |

## Common network policy

All endpoint operations need (1) explicit endpoint/RPC URL, (2) `[app].network_requests_enabled = true`, and (3) `--allow-network`. Tor is not implemented and `tor_enabled=true` fails closed. Querying a public address discloses the address and connection metadata to the chosen provider. Local tests use mocked responses; this release has not broadcast a real transaction as part of validation.

## Bitcoin

Esplora balance/history read one address only. Send selection uses confirmed UTXOs at first receive address, fee-rate estimate and a max-fee cap. It signs P2WPKH locally and demands typed confirmation before POST `/tx`. Change goes to `m/84'/0'/0'/1/0`, currently not scanned. This is a critical limitation: funds are recoverable using the recovery phrase in a compatible wallet, but Vaultsh cannot discover/spend that change yet.

## Ethereum

Address and chain ID are checked first. ETH sends use legacy `gasPrice` + EIP-155 signing on chain ID 1 only, explicit fee cap and exact confirmation text before `eth_sendRawTransaction`. A returned hash is submission acknowledgement, not finality. Other EVM profiles are read-only.

## Solana

The endpoint is checked against Solana Mainnet genesis hash. Amounts use lamports; the signed native SOL transfer is submitted only after exact typed confirmation. A transaction signature does not confirm successful finalization. Token support and confirmation polling are absent.

## Monero

Vaultsh connects only to a loopback official `monero-wallet-rpc`. It validates the locally opened wallet's address as Mainnet, prepares with `do_not_relay=true` and `get_tx_metadata=true`, then submits `tx_metadata` via `relay_tx` only after confirmation. The RPC process must be trusted and correctly configured to a verified Mainnet daemon. Vaultsh does not handle XMR key derivation or seed storage itself.
