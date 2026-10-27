# Configuration reference

Vaultsh configuration is non-secret TOML. Network requests and telemetry are disabled by default. The Bitcoin balance command requires a user-selected endpoint, a config file that enables networking, and the explicit `--allow-network` command-line flag.

## Generate a template

```bash
vaultsh config-init ./vaultsh.toml
```

Use `--force` only when intentionally replacing an existing file:

```bash
vaultsh config-init ./vaultsh.toml --force
```

## Example file

```toml
[app]
app_name = "vaultsh"
telemetry_enabled = false
network_requests_enabled = false
tor_enabled = false
request_timeout_seconds = 15.0
```

Validate it with:

```bash
vaultsh config-check ./vaultsh.toml
```

## Settings

| Key | Type | Default | Validation / meaning |
|---|---|---:|---|
| `app_name` | string | `"vaultsh"` | Must be non-empty and have no surrounding whitespace. |
| `telemetry_enabled` | boolean | `false` | Telemetry is disabled; there is no telemetry pipeline. |
| `network_requests_enabled` | boolean | `false` | Required to permit the optional Bitcoin balance request. It is not sufficient on its own. |
| `tor_enabled` | boolean | `false` | Cannot be true while `network_requests_enabled` is false. Tor transport is not implemented; the balance command refuses to connect when this setting is true. |
| `request_timeout_seconds` | number | `15.0` | Must be between 0.1 and 300 seconds inclusive; used by the read-only Esplora client. |

Only the `[app]` top-level table and the listed keys are accepted. Unknown sections and keys are rejected rather than ignored. Boolean fields must be TOML booleans (`true`/`false`), not quoted strings. Timeout must be numeric, not a boolean.

## Explicitly enabling a balance lookup

The default template deliberately disables networking. To query one address, change only the network setting when you understand the privacy trade-off:

```toml
[app]
app_name = "vaultsh"
telemetry_enabled = false
network_requests_enabled = true
tor_enabled = false
request_timeout_seconds = 15.0
```

Then supply the endpoint and explicit flag for the individual command:

```bash
vaultsh bitcoin balance ADDRESS --endpoint https://esplora.example/api --config ./vaultsh.toml --allow-network
```

Replace the placeholder endpoint with a compatible endpoint you trust. The command sends the address and connection metadata to that endpoint. Vaultsh does not pick a default provider, follow redirects, honor ambient HTTP proxy environment variables, or route traffic through Tor. HTTPS is required for remote hosts; HTTP is accepted only for localhost/loopback.

## Important behavior

- `vaultsh config` displays default in-memory settings. It does not load an arbitrary file.
- `vaultsh config-check PATH` loads and validates the file passed on the command line.
- There is no global `--config` option; only commands that document `--config` consume a config file.
- `network_requests_enabled = true` does not itself authorize a request. The balance command also requires `--allow-network`.
- If `tor_enabled = true`, the balance command refuses to connect because no Tor transport is implemented. It does not silently fall back to a direct request.
- The endpoint is supplied per command and is not stored in a config file.

## Secrets are not configuration

Do not store the vault password, recovery phrase, private keys, API tokens, node credentials, or derived encryption keys in TOML. Use hidden interactive prompts for secrets. Keep vault files and backups out of version control and review `.gitignore` and `git status` before committing.
