# Configuration reference

Vaultsh configuration is non-secret TOML. Defaults are designed to avoid unexpected network communication. The current release validates configuration but does not wire these preferences into a blockchain client, because no live blockchain client is implemented.

## Generate a template

```bash
vaultsh config-init ./vaultsh.toml
```

Use `--force` only if intentionally replacing the existing file:

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
| `telemetry_enabled` | boolean | `false` | Telemetry is disabled in this build; there is no telemetry pipeline. |
| `network_requests_enabled` | boolean | `false` | Future network clients must not assume networking is enabled. |
| `tor_enabled` | boolean | `false` | Cannot be true while `network_requests_enabled` is false. It does not start Tor. |
| `request_timeout_seconds` | number | `15.0` | Must be in the inclusive range 0.1 through 300 seconds. |

Only the `[app]` top-level table and the listed keys are accepted. Unknown sections and keys are rejected rather than ignored. Boolean fields must be TOML booleans (`true`/`false`), not quoted strings. Timeout must be numeric, not a boolean.

## Important behavior

- `vaultsh config` displays the default in-memory configuration.
- `vaultsh config-check PATH` loads and validates the file passed on the command line.
- There is no global `--config` option in this release and the other commands do not automatically load a config file.
- Setting `network_requests_enabled = true` does not create a network feature or itself authorize a request. Future network calls must also require explicit user intent via the network-policy helper.
- `tor_enabled = true` is just a validated preference until a client transport is implemented. Vaultsh 0.3.0 does not start Tor, check a SOCKS listener, or route traffic through it.

## Secrets are not configuration

Do not store the vault password, recovery phrase, private keys, API tokens, node credentials, or derived encryption keys in a TOML file. Use hidden interactive prompts for secrets. Keep vault files and backups outside version control; review `.gitignore` and `git status` before committing.
