# Network adapters

This document describes the implementation in Vaultsh **0.6.0**. These are read-only query adapters, not complete wallet integrations. The project is pre-alpha and unaudited.

## Supported networks

| Network key | Network | Chain ID | Native asset shown | Implemented capability |
|---|---|---:|---|---|
| `bitcoin` | Bitcoin Mainnet | — | BTC | Address balance and first-page transaction history through an Esplora-compatible REST API |
| `ethereum` | Ethereum Mainnet | `1` | ETH | Native balance at the latest block through JSON-RPC 2.0 |
| `polygon` | Polygon PoS Mainnet | `137` | POL | Native balance at the latest block through JSON-RPC 2.0 |
| `arbitrum` | Arbitrum One | `42161` | ETH | Native balance at the latest block through JSON-RPC 2.0 |
| `optimism` | Optimism Mainnet | `10` | ETH | Native balance at the latest block through JSON-RPC 2.0 |
| `base` | Base Mainnet | `8453` | ETH | Native balance at the latest block through JSON-RPC 2.0 |
| `monero` | Monero | — | — | Not implemented |

The EVM allow-list is deliberately explicit. A network being EVM-compatible does not automatically mean Vaultsh supports it. Mainnet profiles and chain IDs should be confirmed with each network's official documentation before changing this list.

## Network permission model

Each remote query requires all of the following:

1. An explicit `--endpoint URL` selected by the user.
2. A supplied TOML file with `[app].network_requests_enabled = true`.
3. The command-line flag `--allow-network`.
4. `tor_enabled = false`, because Tor transport is not implemented. If set to `true`, Vaultsh refuses the query instead of making a direct connection.

Remote endpoints must use HTTPS. Plain HTTP is accepted only for localhost or loopback IPs. URL credentials, query strings, fragments, control characters, and dot-segment paths are rejected. Redirects are blocked, environment proxy variables are ignored, response sizes are bounded, and requests have timeouts. Some providers place access tokens in the URL path; do not disclose such URLs in logs, screenshots, or issue reports. The CLI prints only the endpoint hostname.

## Bitcoin Mainnet / Esplora

Commands:

```bash
vaultsh bitcoin balance ADDRESS --endpoint https://YOUR-ESPLORA/api \
  --config ./vaultsh.toml --allow-network

vaultsh bitcoin history ADDRESS --endpoint https://YOUR-ESPLORA/api \
  --config ./vaultsh.toml --allow-network --limit 10
```

The balance endpoint is `GET /address/{address}`. Confirmed balance and net mempool change are shown in satoshis and BTC, using integer arithmetic. The client validates the supported Mainnet address using `embit`, response schema and address equality, and enforces response/time limits.

The history endpoint is `GET /address/{address}/txs`. It returns at most 25 records from the first provider response page for one address. Vaultsh validates transaction IDs, status fields, required block metadata for confirmed transactions, duplicate entries, and optional fee values. There is no pagination, address discovery, wallet-wide aggregation, or complete history guarantee.

Reference: [Esplora API specification](https://github.com/Blockstream/esplora/blob/master/API.md).

## EVM JSON-RPC

Ethereum-specific shortcut:

```bash
vaultsh ethereum balance 0xYOUR_ADDRESS --endpoint https://YOUR-ETH-RPC \
  --config ./vaultsh.toml --allow-network
```

Generic profile-selected command:

```bash
vaultsh evm balance 0xYOUR_ADDRESS --chain polygon \
  --endpoint https://YOUR-POLYGON-RPC --config ./vaultsh.toml --allow-network
```

Supported `--chain` values are `ethereum`, `polygon`, `arbitrum`, `optimism`, and `base`. For each selected profile, the client:

1. Validates an address with a `0x` prefix and exactly 40 hexadecimal characters. Lowercase/uppercase forms are accepted; mixed-case forms must pass EIP-55 validation.
2. Calls `eth_chainId` and compares it to the expected profile ID before making the balance query.
3. Calls `eth_getBalance` with `[ADDRESS, "latest"]`.
4. Validates JSON-RPC 2.0, request ID, response shape, and hex quantity; then formats the 18-decimal native asset without floating-point arithmetic.

The profile mapping is:

| `--chain` | Expected `eth_chainId` | Display unit |
|---|---:|---|
| `ethereum` | `0x1` (1) | ETH / wei |
| `polygon` | `0x89` (137) | POL / base units |
| `arbitrum` | `0xa4b1` (42161) | ETH / wei |
| `optimism` | `0xa` (10) | ETH / wei |
| `base` | `0x2105` (8453) | ETH / wei |

References: [Ethereum JSON-RPC API](https://ethereum.org/developers/docs/apis/json-rpc/), [EIP-55 checksum specification](https://eips.ethereum.org/EIPS/eip-55), [Arbitrum chain information](https://docs.arbitrum.io/chain-info), [Base `eth_chainId`](https://docs.base.org/base-chain/api-reference/ethereum-json-rpc-api/eth_chainId), and [Optimism chain information](https://docs.optimism.io/), plus [Polygon PoS Mainnet setup information](https://support.polygon.technology/support/solutions/articles/82000889434-how-to-add-polygon-mainnet-on-metamask-). Polygon PoS Mainnet uses chain ID 137; the current native token is displayed as POL.

## Explicit limitations

- EVM balance results are supplied by the selected JSON-RPC provider. Vaultsh does not verify state proofs or independently prove the returned balance.
- A query exposes the requested address and connection metadata to the selected endpoint. It does not use Tor, and public chain activity may be correlated independently of network transport.
- EVM wallet generation/recovery, EVM key derivation and storage, ERC-20 tokens, EVM transaction history, contract calls beyond the described read-only balance methods, gas estimation, transaction previews, signing, and broadcasting are not implemented.
- Only the listed EVM mainnet profiles are accepted. Testnets and other EVM networks are not automatically supported.
- Monero is not implemented. Monero has distinct key, address, and privacy models and must not be treated as an EVM or Bitcoin variant.
- The presence of an adapter protocol or package directory does not imply functional support.
