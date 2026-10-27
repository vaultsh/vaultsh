# Configuration — Vaultsh 1.0.0-beta.1

`vaultsh config-init ./vaultsh.toml` creates non-secret configuration; `vaultsh config-check ./vaultsh.toml` validates it. Do not store passphrases, mnemonic phrases, private keys, RPC passwords or tokens in TOML.

```toml
[app]
app_name = "vaultsh"
telemetry_enabled = false
network_requests_enabled = false
tor_enabled = false
request_timeout_seconds = 15.0
```

| Setting | Default | Meaning |
|---|---:|---|
| `app_name` | `vaultsh` | Display/metadata name only |
| `telemetry_enabled` | `false` | Telemetry is not implemented; keep disabled |
| `network_requests_enabled` | `false` | Permission gate for remote endpoints and local Monero RPC calls |
| `tor_enabled` | `false` | Tor transport is not implemented; if true, network actions refuse to run |
| `request_timeout_seconds` | `15.0` | Request timeout, validated between 0.1 and 300 seconds |

Both configuration permission and command-line intent are required: `--config ./vaultsh.toml --allow-network`. The `--allow-network` flag is a per-command authorization, not a persistent setting. Endpoints are supplied explicitly on commands. Endpoint operators may see public addresses and connection metadata.

For Monero, `--rpc-url` defaults to loopback `http://127.0.0.1:18082/json_rpc`; the client rejects non-loopback URLs. Monero wallet-RPC credentials are prompted/handled separately and should not be saved to this file. Configure the RPC process with authentication if appropriate and never expose it outside loopback.
