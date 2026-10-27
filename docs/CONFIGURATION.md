# Configuration reference

This document describes `AppConfig` and TOML validation in Vaultsh **0.6.0**.

## Create and validate a config file

```bash
vaultsh config-init ./vaultsh.toml
vaultsh config-check ./vaultsh.toml
```

`config-init` refuses to overwrite an existing path unless `--force` is supplied. A configuration file contains preferences, not secret material.

## Example

```toml
[app]
app_name = "vaultsh"
telemetry_enabled = false
network_requests_enabled = false
tor_enabled = false
request_timeout_seconds = 15.0
```

The generated example keeps network requests disabled. Change `network_requests_enabled` to `true` only when you are ready to send a public address to a provider you selected.

## Settings

| Key | Type | Default | Meaning |
|---|---|---:|---|
| `app_name` | string | `"vaultsh"` | Display/application identifier; must be non-empty and trimmed |
| `telemetry_enabled` | boolean | `false` | Telemetry is disabled in this build; there is no analytics sender |
| `network_requests_enabled` | boolean | `false` | Configuration permission for read-only Bitcoin/EVM requests |
| `tor_enabled` | boolean | `false` | If true, network commands refuse direct connections because Tor transport is not implemented |
| `request_timeout_seconds` | number | `15.0` | Per-request timeout, inclusive range 0.1–300 seconds |

Unknown top-level sections and unknown keys in `[app]` are rejected. Booleans are not accepted as numeric timeouts. `tor_enabled = true` is rejected unless network requests are enabled, but enabling both does **not** mean Tor works; current network commands still refuse to connect until Tor transport is implemented.

## Required dual opt-in

For each remote read-only operation, both conditions must be true:

1. `network_requests_enabled = true` in the TOML file passed via `--config`.
2. `--allow-network` appears on the command line.

Example:

```bash
vaultsh bitcoin balance ADDRESS --endpoint https://YOUR-ESPLORA/api \
  --config ./vaultsh.toml --allow-network

vaultsh bitcoin history ADDRESS --endpoint https://YOUR-ESPLORA/api \
  --config ./vaultsh.toml --allow-network --limit 10

vaultsh ethereum balance 0xYOUR_ADDRESS --endpoint https://YOUR-ETH-RPC \
  --config ./vaultsh.toml --allow-network

vaultsh evm balance 0xYOUR_ADDRESS --chain polygon \
  --endpoint https://YOUR-POLYGON-RPC --config ./vaultsh.toml --allow-network
```

There is no default public endpoint. The Bitcoin client expects an Esplora-compatible REST endpoint. The EVM client expects a JSON-RPC 2.0 endpoint and refuses a response whose `eth_chainId` does not match the chosen profile (`ethereum`, `polygon`, `arbitrum`, `optimism`, or `base`).

## Endpoint and privacy rules

- Remote endpoints must use HTTPS. Plain HTTP is allowed only for localhost/loopback IP addresses, primarily for a self-hosted local node.
- Credentials embedded in URLs, query strings, fragments, control characters, and path dot-segments are rejected.
- Redirects are not followed and environment proxy variables are ignored.
- Endpoint choice is not stored in `AppConfig`; it is passed explicitly on each command.
- The selected endpoint receives the queried public address and connection metadata. Tor is not supported; the client does not automatically route through a proxy.
- Some RPC providers put tokens into URL paths. Treat such values as secrets; avoid them if possible and do not paste them into issue trackers or screenshots. EVM CLI output displays the host only.

Do not put passwords, recovery phrases, private keys, seeds, vault contents, or API credentials in TOML files committed to source control.
