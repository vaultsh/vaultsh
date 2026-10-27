# CLI reference

The examples below describe Vaultsh **0.4.5**. Commands that open a vault prompt for passwords without echoing them. Commands that make network requests need both an explicit CLI opt-in and permission in the supplied configuration.

## Global commands

| Command | Purpose |
|---|---|
| `vaultsh` | Show the landing screen and pre-alpha warning. |
| `vaultsh --help` | Show top-level help. |
| `vaultsh about` | Display project scope and implementation status. |
| `vaultsh networks` | Show implemented and planned network functionality. |
| `vaultsh privacy` | Display privacy defaults and current network limitations. |
| `vaultsh config` | Display default, non-secret settings. It does not load a config file. |
| `vaultsh version` | Print the installed version. |
| `vaultsh config-init PATH [--force]` | Create a non-secret TOML template. `--force` permits replacing a file. |
| `vaultsh config-check PATH` | Parse and validate a TOML config, then print recognized non-secret values. |

Use `vaultsh <command> --help` for the installed command's option list.

## Vault commands

### `vaultsh vault init PATH [--label LABEL]`

Creates an encrypted metadata vault. Password entry and confirmation are hidden. New vault passwords must be at least 12 characters; this is a minimum length, not a measure of entropy. An existing destination is not overwritten.

```bash
vaultsh vault init ./main.vault --label "Main vault"
```

### `vaultsh vault check PATH`

Prompts for the password, decrypts and validates the inner JSON document, then shows the vault label, UUID, creation timestamp, schema version, and wallet-record count. It does not query a blockchain or reveal recovery phrases.

```bash
vaultsh vault check ./main.vault
```

### `vaultsh vault backup SOURCE DESTINATION [--overwrite]`

Copies encrypted file bytes to a new path without decrypting the source. The destination is not replaced unless `--overwrite` is provided. This command does not prove the password is correct or validate the decrypted document; run `vaultsh vault check` against the restored backup.

```bash
vaultsh vault backup ./main.vault ./backups/main.vault.backup
```

### `vaultsh vault restore SOURCE DESTINATION [--overwrite]`

Copies an encrypted backup into a vault path. Destination replacement is refused unless `--overwrite` is supplied.

```bash
vaultsh vault restore ./backups/main.vault.backup ./restored.vault
vaultsh vault check ./restored.vault
```

## Wallet commands

Wallet creation and recovery below operate locally/offline. This release supports Bitcoin Mainnet only, and its balance lookup is a separate explicit network command.

### `vaultsh wallet create --vault PATH [--label LABEL]`

Creates a 12-word English BIP-39 phrase using 128 bits of operating-system entropy, derives the first BIP-84 Native SegWit receive address, and stores the phrase inside the encrypted vault. The phrase is displayed after creation.

```bash
vaultsh wallet create --vault ./main.vault --label "Bitcoin Main"
```

Record the phrase offline and never share it. Do not send funds to this pre-alpha software.

### `vaultsh wallet recover --vault PATH [--label LABEL]`

Prompts for a recovery phrase with hidden input, then prompts for the vault password. It accepts valid English BIP-39 phrases of 12 or 24 words. The optional BIP-39 passphrase must be empty.

```bash
vaultsh wallet recover --vault ./main.vault --label "Recovered wallet"
```

### `vaultsh wallet list --vault PATH`

Decrypts and validates the vault, then lists public metadata: wallet ID, label, network, first receive address, and derivation path. Recovery phrases are not returned by the listing API or printed by this command. This command does not query the blockchain.

```bash
vaultsh wallet list --vault ./main.vault
```

### `vaultsh wallet recovery-phrase WALLET_ID --vault PATH`

Requires explicit confirmation and the vault password before printing the requested recovery phrase. Avoid using it during screen sharing, terminal recording, or on an untrusted machine.

```bash
vaultsh wallet recovery-phrase WALLET_ID --vault ./main.vault
```

Replace `WALLET_ID` with an ID shown by `wallet list`.

## Bitcoin balance command

### `vaultsh bitcoin balance ADDRESS --endpoint URL --config PATH --allow-network`

Queries one Bitcoin Mainnet address through a user-selected Esplora-compatible endpoint. The request is read-only and uses `GET /address/{address}`. The client reads the endpoint's confirmed and mempool transaction-output statistics, calculates values in integer satoshis, and displays BTC values without floating-point arithmetic.

```bash
vaultsh config-init ./vaultsh.toml
# Edit vaultsh.toml: set network_requests_enabled = true
vaultsh bitcoin balance ADDRESS \
  --endpoint https://esplora.example/api \
  --config ./vaultsh.toml \
  --allow-network
```

`esplora.example` is a placeholder; replace it with a compatible endpoint you trust. Vaultsh does not select a default provider.

Both conditions below are required before the command constructs a client:

1. `[app].network_requests_enabled = true` in the TOML file supplied by `--config`.
2. The command-line flag `--allow-network`.

The command also refuses to connect if `tor_enabled = true`, because this release does not implement Tor transport. It will not silently fall back to a direct connection in that case.

### Endpoint and privacy behavior

- Remote endpoints must use HTTPS. Plain HTTP is accepted only for `localhost` or a loopback IP address, mainly for a local Esplora service.
- Endpoint URL credentials, query strings, fragments, malformed ports, and dot-segment paths are rejected.
- HTTP redirects are not followed. Ambient `HTTP_PROXY`/`HTTPS_PROXY` environment variables are not used by this client.
- The request has a timeout and a bounded response size. Malformed JSON, unexpected fields, invalid satoshi values, and a response for another address are rejected.
- The address and connection metadata (potentially including your IP address) are disclosed to the selected endpoint. Choose a trustworthy endpoint; a self-hosted service may reduce third-party exposure but still requires correct configuration and host security.
- Returned numbers are service-provided data, not a proof of ownership or a cryptographic proof that the result is complete or current. Only the supplied address is queried; no wallet-wide address discovery or balance aggregation is performed.

No transaction data is submitted. Transaction construction, signing, broadcasting, fee estimation, and complete history are not implemented.

## Configuration commands

### `vaultsh config-init PATH [--force]`

Writes a non-secret TOML template with `[app]`, `app_name`, `telemetry_enabled`, `network_requests_enabled`, `tor_enabled`, and `request_timeout_seconds`.

### `vaultsh config-check PATH`

Validates TOML syntax, allowed sections and keys, value types, timeout range, and the rule that `tor_enabled = true` requires `network_requests_enabled = true`. Unknown keys are rejected rather than silently ignored.

A valid config does not automatically make a network request. Only the Bitcoin balance command currently uses network settings, and it still requires `--allow-network`.

## Errors and exit behavior

Expected operational errors display a human-readable message and exit non-zero. Do not rely on exact exception wording as a stable API; the project is pre-alpha and error text may change. Network errors are intentionally summarized and do not include recovery phrases or vault contents.

## Not available in 0.4.5

- Address-gap discovery, used-address scanning, wallet-wide balance aggregation, or transaction history.
- Bitcoin Core RPC support or node administration.
- Fee estimation, transaction construction, PSBT signing, or broadcasting.
- Ethereum/EVM and Monero wallet support.
- Tor process control or traffic routing.

A network adapter or Tor settings helper does not imply the associated functionality is complete.
