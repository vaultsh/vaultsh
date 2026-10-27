# CLI reference

This reference describes the commands in Vaultsh **0.6.0**. Use `vaultsh --help` or `vaultsh COMMAND --help` for the installed build's generated help text.

## General commands

### `vaultsh`

Shows a landing screen and the pre-alpha warning.

### `vaultsh version`

Prints the installed version.

### `vaultsh about`

Describes implemented capabilities and major gaps.

### `vaultsh networks`

Lists Bitcoin Mainnet and five supported EVM mainnet profiles, plus the unimplemented Monero adapter.

### `vaultsh privacy`

Shows privacy defaults and warns that network queries disclose addresses and connection metadata to the selected endpoint. Tor transport is not implemented.

### `vaultsh config`

Shows default non-secret config values without reading or displaying secrets.

## Configuration commands

### `vaultsh config-init PATH [--force]`

Writes a sample TOML configuration. Refuses to replace an existing file unless `--force` is passed.

### `vaultsh config-check PATH`

Validates TOML syntax, known sections/keys, setting types, timeout range, and Tor/network consistency.

## Vault commands

### `vaultsh vault init PATH [--label LABEL]`

Creates a new encrypted metadata vault. Prompts for a hidden password twice. The password must be at least 12 characters. Existing paths are not overwritten.

### `vaultsh vault check PATH`

Prompts for the password, authenticates/decrypts the file, validates the inner schema, and displays public metadata only.

### `vaultsh vault backup SOURCE DESTINATION [--overwrite]`

Creates a byte-for-byte copy of an encrypted vault. The source is not decrypted by the copy operation.

### `vaultsh vault restore SOURCE DESTINATION [--overwrite]`

Restores an encrypted backup to a new destination path by default. Run `vaultsh vault check DESTINATION` afterward.

## Bitcoin wallet commands

### `vaultsh wallet create --vault PATH [--label LABEL]`

Creates an offline Bitcoin Mainnet wallet using a 12-word English BIP-39 phrase and derives the first BIP-84 Native SegWit address at `m/84'/0'/0'/0/0`. The recovery phrase is displayed once and also stored inside the encrypted vault payload.

### `vaultsh wallet recover --vault PATH [--label LABEL]`

Imports a valid English BIP-39 12- or 24-word phrase with empty BIP-39 passphrase. Input is hidden. It stores the phrase inside the encrypted vault and derives the same supported first receive address.

### `vaultsh wallet list --vault PATH`

Prompts to unlock the vault and displays public wallet metadata only; it does not show recovery phrases.

### `vaultsh wallet recovery-phrase WALLET_ID --vault PATH`

Requires an explicit confirmation and vault password before displaying the phrase. Use only in a private place; terminal output may be captured by screenshots, logs, or screen-recording tools.

## Bitcoin read-only commands

Both Bitcoin network commands require a user-supplied Esplora endpoint, a config file with `network_requests_enabled = true`, and `--allow-network`. If `tor_enabled = true`, the command refuses to make a direct request.

### `vaultsh bitcoin balance ADDRESS --endpoint URL --config PATH --allow-network`

Queries `GET /address/{address}` for one Bitcoin Mainnet address. Displays confirmed balance, net unconfirmed change, and estimated total in satoshis and BTC, using integer arithmetic.

### `vaultsh bitcoin history ADDRESS --endpoint URL --config PATH [--limit N] --allow-network`

Queries `GET /address/{address}/txs` and displays at most 25 entries from the first response page. `--limit` defaults to 10 and must be from 1 to 25. Output includes transaction ID, confirmation state, block height/time (for confirmed entries), and fee when supplied.

This is not a complete wallet history, does not paginate, and does not discover additional addresses.

## EVM read-only balance commands

### `vaultsh ethereum balance ADDRESS --endpoint URL --config PATH --allow-network`

Validates a 20-byte `0x` address; mixed-case forms must pass EIP-55. Sends `eth_chainId` first and proceeds only when it matches the selected profile. Then calls `eth_getBalance` with `[ADDRESS, "latest"]`. Balances are displayed using integer-only 18-decimal formatting.

`vaultsh ethereum balance` always selects Ethereum Mainnet (chain ID `1`, ETH). The generic command supports these exact profiles:

| `--chain` | Network | Chain ID | Native asset |
|---|---|---:|---|
| `ethereum` | Ethereum Mainnet | `1` | ETH |
| `polygon` | Polygon PoS Mainnet | `137` | POL |
| `arbitrum` | Arbitrum One | `42161` | ETH |
| `optimism` | Optimism Mainnet | `10` | ETH |
| `base` | Base Mainnet | `8453` | ETH |

Example:

```bash
vaultsh evm balance 0xYOUR_ADDRESS --chain arbitrum \
  --endpoint https://YOUR-ARBITRUM-RPC --config ./vaultsh.toml --allow-network
```

This command queries native assets only. It does not create/import EVM wallets, derive private keys, query ERC-20 token contracts, retrieve EVM transaction history, estimate gas, or build/sign/broadcast transactions.

## Operational behavior and errors

- No public provider is chosen automatically.
- Remote HTTPS endpoints are required; plain HTTP is limited to loopback.
- Requests use timeouts and bounded response bodies, reject redirects, and ignore environment proxy variables.
- RPC response IDs, schemas, quantities, addresses, and chain ID are validated. Provider error messages are not echoed verbatim.
- Expected failures exit non-zero and show a sanitized message. Error text is not a stable API in pre-alpha.
- Read-only results are provider-supplied data, not proof of address ownership or a cryptographic proof of balance.
