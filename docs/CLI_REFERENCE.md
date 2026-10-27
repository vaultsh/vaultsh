# CLI reference — Vaultsh 1.0.0-beta.1

Run `vaultsh --help` and `vaultsh COMMAND --help` for installed help. Put `--lang pl` or `--lang ru` before the command.

## General and setup

```bash
vaultsh --lang pl
vaultsh version
vaultsh about
vaultsh networks
vaultsh privacy
vaultsh config-init ./vaultsh.toml
vaultsh config-check ./vaultsh.toml
```

## Vault and wallet records

```bash
vaultsh vault init ./main.vault --label "Main vault"
vaultsh vault check ./main.vault
vaultsh vault backup ./main.vault ./main.vault.backup
vaultsh vault restore ./main.vault.backup ./restored.vault
vaultsh wallet create --vault ./main.vault --label "BTC wallet" --network bitcoin
vaultsh wallet create --vault ./main.vault --label "ETH wallet" --network ethereum
vaultsh wallet create --vault ./main.vault --label "SOL wallet" --network solana
vaultsh wallet recover --vault ./main.vault --network ethereum
vaultsh wallet list --vault ./main.vault
vaultsh wallet recovery-phrase --vault ./main.vault --wallet-id WALLET_ID
vaultsh wallet qr --vault ./main.vault --wallet-id WALLET_ID --output ./address.png
vaultsh qr PUBLIC_ADDRESS --output ./address.png
```

Recovery-phrase commands display secret material. Protect the screen and never paste a phrase into an issue, chat or screenshot.

## Network permission

Use an explicit endpoint and both network opt-ins for every remote operation:

```toml
[app]
app_name = "vaultsh"
telemetry_enabled = false
network_requests_enabled = true
tor_enabled = false
request_timeout_seconds = 15.0
```

Add `--config ./vaultsh.toml --allow-network` to network commands. Tor transport is not implemented; if `tor_enabled = true`, Vaultsh fails closed.

## Bitcoin

```bash
vaultsh bitcoin balance ADDRESS --endpoint https://YOUR-ESPLORA/api --config ./vaultsh.toml --allow-network
vaultsh bitcoin history ADDRESS --endpoint https://YOUR-ESPLORA/api --config ./vaultsh.toml --allow-network --limit 10
vaultsh bitcoin send --wallet-id WALLET_ID --vault ./main.vault --to bc1qRECIPIENT --amount 0.0001 --endpoint https://YOUR-ESPLORA/api --config ./vaultsh.toml --allow-network --max-fee-sats 100000
```

**Do not use BTC send with real funds:** only first receive-address confirmed UTXOs are scanned and change to `/1/0` is not discovered by Vaultsh yet. Transaction requires exact typed confirmation and never has a `--yes` bypass.

## Ethereum Mainnet

```bash
vaultsh ethereum balance 0xADDRESS --endpoint https://YOUR-ETH-RPC --config ./vaultsh.toml --allow-network
vaultsh ethereum send --wallet-id WALLET_ID --vault ./main.vault --to 0xRECIPIENT --amount 0.001 --endpoint https://YOUR-ETH-RPC --config ./vaultsh.toml --allow-network --max-fee-eth 0.1
```

Only native ETH on chain ID 1 is sendable, using a legacy EIP-155 `gasPrice` transaction.

## Other EVM balance profiles

```bash
vaultsh evm balance 0xADDRESS --chain polygon --endpoint https://YOUR-RPC --config ./vaultsh.toml --allow-network
```

Supported read-only profiles: `ethereum`, `polygon`, `arbitrum`, `optimism`, `base`. Sending is only implemented for Ethereum Mainnet.

## Solana Mainnet

```bash
vaultsh solana balance SOL_ADDRESS --endpoint https://YOUR-SOLANA-RPC --config ./vaultsh.toml --allow-network
vaultsh solana send --wallet-id WALLET_ID --vault ./main.vault --to SOL_RECIPIENT --amount 0.01 --endpoint https://YOUR-SOLANA-RPC --config ./vaultsh.toml --allow-network --max-fee-sol 0.01
```

Only native SOL transfers; SPL tokens and finality polling are not implemented. `sendTransaction` returning a signature means submitted, not confirmed.

## Monero through local wallet RPC

Install and configure the official `monero-wallet-rpc` yourself. Keep it on loopback, verify its daemon and Mainnet settings, and do not expose its port publicly.

```bash
vaultsh monero create-wallet MY_WALLET --config ./vaultsh.toml --allow-network
vaultsh monero open-wallet MY_WALLET --config ./vaultsh.toml --allow-network
vaultsh monero address --config ./vaultsh.toml --allow-network
vaultsh monero balance --config ./vaultsh.toml --allow-network
vaultsh monero send --to XMR_MAINNET_ADDRESS --amount 0.01 --config ./vaultsh.toml --allow-network
vaultsh monero close-wallet --config ./vaultsh.toml --allow-network
```

Default local endpoint is `http://127.0.0.1:18082/json_rpc`. Monero seed/files are managed by `monero-wallet-rpc`, not stored in the Vaultsh vault. The send workflow prepares a transaction with no relay, shows amount/fee, asks typed confirmation, and relays the returned metadata.

## QR codes

`vaultsh qr ADDRESS --output path.png` outputs a PNG; without output it attempts to render a terminal QR. It accepts address-shaped BTC/EVM/XMR/SOL public strings only; format recognition is not a universal checksum or ownership proof.
