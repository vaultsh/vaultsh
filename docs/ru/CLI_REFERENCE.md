# CLI — Vaultsh 1.0.0-beta.1

Запустите `vaultsh --help` и `vaultsh COMMAND --help`. Параметр языка `--lang pl` или `--lang ru` указывается до команды.

```bash
vaultsh config-init ./vaultsh.toml
vaultsh config-check ./vaultsh.toml
vaultsh vault init ./main.vault --label "My Vault"
vaultsh vault check ./main.vault
vaultsh wallet create --vault ./main.vault --label BTC --network bitcoin
vaultsh wallet create --vault ./main.vault --label ETH --network ethereum
vaultsh wallet create --vault ./main.vault --label SOL --network solana
vaultsh wallet list --vault ./main.vault
vaultsh wallet qr --vault ./main.vault --wallet-id WALLET_ID --output ./address.png
vaultsh qr PUBLIC_ADDRESS --output ./address.png
```

Для сетевого действия TOML должен разрешать `network_requests_enabled = true`; укажите endpoint и `--config ./vaultsh.toml --allow-network`. Если `tor_enabled=true`, запросы блокируются.

BTC:
```bash
vaultsh bitcoin balance ADDRESS --endpoint https://YOUR-ESPLORA/api --config ./vaultsh.toml --allow-network
vaultsh bitcoin history ADDRESS --endpoint https://YOUR-ESPLORA/api --config ./vaultsh.toml --allow-network --limit 10
vaultsh bitcoin send --wallet-id WALLET_ID --vault ./main.vault --to bc1qRECIPIENT --amount 0.0001 --endpoint https://YOUR-ESPLORA/api --config ./vaultsh.toml --allow-network --max-fee-sats 100000
```
**Не отправляйте реальные BTC:** обнаруживаются только UTXO первого receive-адреса; change `/1/0` не сканируется.

ETH Mainnet:
```bash
vaultsh ethereum balance 0xADDRESS --endpoint https://YOUR-ETH-RPC --config ./vaultsh.toml --allow-network
vaultsh ethereum send --wallet-id WALLET_ID --vault ./main.vault --to 0xRECIPIENT --amount 0.001 --endpoint https://YOUR-ETH-RPC --config ./vaultsh.toml --allow-network --max-fee-eth 0.1
vaultsh evm balance 0xADDRESS --chain polygon --endpoint https://YOUR-RPC --config ./vaultsh.toml --allow-network
```
Только нативный ETH Mainnet с legacy `gasPrice`; другие EVM-сети только для чтения.

Solana:
```bash
vaultsh solana balance SOL_ADDRESS --endpoint https://YOUR-SOL-RPC --config ./vaultsh.toml --allow-network
vaultsh solana send --wallet-id WALLET_ID --vault ./main.vault --to SOL_RECIPIENT --amount 0.01 --endpoint https://YOUR-SOL-RPC --config ./vaultsh.toml --allow-network --max-fee-sol 0.01
```
Только SOL; нет SPL и polling финальности.

Monero требует отдельно установленный официальный `monero-wallet-rpc` на loopback:
```bash
vaultsh monero create-wallet MY_WALLET --config ./vaultsh.toml --allow-network
vaultsh monero open-wallet MY_WALLET --config ./vaultsh.toml --allow-network
vaultsh monero address --config ./vaultsh.toml --allow-network
vaultsh monero balance --config ./vaultsh.toml --allow-network
vaultsh monero send --to XMR_MAINNET_ADDRESS --amount 0.01 --config ./vaultsh.toml --allow-network
vaultsh monero close-wallet --config ./vaultsh.toml --allow-network
```
XMR seed/файлы хранятся снаружи хранилища Vaultsh. Любая отправка требует обзора и точного текстового подтверждения.
