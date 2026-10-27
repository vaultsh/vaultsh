# CLI reference

The examples below describe version 0.3.0. Commands that touch a vault normally prompt for a password without echoing it. Exact Rich formatting can vary by terminal width and platform.

## Global commands

| Command | Purpose |
|---|---|
| `vaultsh` | Show the landing screen and a pre-alpha warning. |
| `vaultsh --help` | Show top-level help. |
| `vaultsh about` | Display scope and current implementation status. |
| `vaultsh networks` | Show current and planned network support. |
| `vaultsh privacy` | Display privacy defaults and explain current network limitations. |
| `vaultsh config` | Display default non-secret settings. This does not load an arbitrary config file. |
| `vaultsh version` | Print the installed version. |
| `vaultsh config-init PATH [--force]` | Create a non-secret TOML template; `--force` permits replacing an existing file. |
| `vaultsh config-check PATH` | Parse and validate a TOML config and print recognized non-secret values. |

Use `vaultsh <command> --help` for the help exposed by the installed version.

## Vault commands

### `vaultsh vault init PATH [--label LABEL]`

Creates an empty encrypted metadata vault. Password entry and confirmation are hidden. New vault passwords must be at least 12 characters; the application does not measure password entropy. Existing targets are not overwritten.

```bash
vaultsh vault init ./main.vault --label "Main vault"
```

### `vaultsh vault check PATH`

Prompts for the password, decrypts and validates the inner JSON document, then shows the vault label, UUID, creation timestamp, schema version, and wallet-record count. It does not print recovery phrases, query the blockchain, or test the funds at any address.

```bash
vaultsh vault check ./main.vault
```

### `vaultsh vault backup SOURCE DESTINATION [--overwrite]`

Copies the encrypted file bytes to a new path without decrypting the source. Destination replacement is refused by default. `--overwrite` deliberately permits replacing an existing destination.

```bash
vaultsh vault backup ./main.vault ./backups/main.vault.backup
```

The backup command checks the encrypted-file marker and file size, not password correctness or the inner document schema. To validate a backup, restore it to a distinct path and run `vaultsh vault check`.

### `vaultsh vault restore SOURCE DESTINATION [--overwrite]`

Copies an encrypted backup to a vault path. Destination replacement is refused unless `--overwrite` is supplied.

```bash
vaultsh vault restore ./backups/main.vault.backup ./restored.vault
vaultsh vault check ./restored.vault
```

## Wallet commands

All wallet commands in this release support Bitcoin Mainnet only and work offline.

### `vaultsh wallet create --vault PATH [--label LABEL]`

Creates a new 12-word English BIP-39 phrase using 128 bits of OS entropy, derives the first BIP-84 native-SegWit receive address, and stores the wallet record in the encrypted vault. The vault must already exist. The command displays the phrase when creation succeeds.

```bash
vaultsh wallet create --vault ./main.vault --label "Bitcoin Main"
```

**Immediately record the recovery phrase offline.** Anyone who gets the phrase can control the wallet. Do not send funds to this pre-alpha release.

### `vaultsh wallet recover --vault PATH [--label LABEL]`

Prompts for a recovery phrase with input hidden, then prompts for the vault password. It accepts valid English BIP-39 phrases of 12 or 24 words. The optional BIP-39 passphrase must be empty. A wallet that used a non-empty passphrase will produce a different address here.

```bash
vaultsh wallet recover --vault ./main.vault --label "Recovered wallet"
```

### `vaultsh wallet list --vault PATH`

Decrypts the vault and lists public metadata: wallet ID, label, network, first receive address, and derivation path. Mnemonics are not returned by the storage listing API or displayed by this command.

```bash
vaultsh wallet list --vault ./main.vault
```

Listing does not query the blockchain. An address may be unused, used, funded, or empty; Vaultsh does not know which.

### `vaultsh wallet recovery-phrase WALLET_ID --vault PATH`

Asks for explicit confirmation, then the vault password, before printing the stored phrase. Obtain the wallet ID from `wallet list`. Cancel the confirmation to avoid displaying the secret.

```bash
vaultsh wallet recovery-phrase 00000000-0000-4000-8000-000000000000 --vault ./main.vault
```

The UUID above is an example shape only; use the ID reported for your actual wallet. Avoid this command during screen sharing, recording, or on an untrusted system.

## Configuration commands

### `vaultsh config-init PATH [--force]`

Writes a TOML template with `[app]`, `app_name`, `telemetry_enabled`, `network_requests_enabled`, `tor_enabled`, and `request_timeout_seconds`. The file must contain preferences only; never put passwords, mnemonics, private keys, tokens, or derived keys into it.

### `vaultsh config-check PATH`

Validates the TOML syntax, allowed sections, allowed setting names, value types, timeout range, and the rule that enabling Tor settings also requires enabling network requests. Unknown keys are rejected to prevent misspellings from being silently ignored.

This is configuration validation, not activation of networking. No command in version 0.3.0 uses the TOML file to perform blockchain requests because no live blockchain client is implemented.

## Exit behavior and errors

On expected operational errors, commands display a human-readable message and exit non-zero. Do not rely on exact exception wording as a stable API; the project is pre-alpha and error messages may change.

## Not available in 0.3.0

There are no commands for balance, transaction history, UTXOs, fee estimation, transaction signing/broadcasting, Ethereum/EVM, Monero, Tor process control, or node setup. A planned network adapter or proxy setting does not mean its associated feature is operational.
