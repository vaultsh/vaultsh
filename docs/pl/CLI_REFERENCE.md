# Referencja CLI — Vaultsh 1.0.0-beta.1

Sprawdź `vaultsh --help` i `vaultsh COMMAND --help`. Opcje językowe `--lang pl` / `--lang ru` podaj przed komendą.

## Konfiguracja i sejf
```bash
vaultsh config-init ./vaultsh.toml
vaultsh config-check ./vaultsh.toml
vaultsh vault init ./main.vault --label "Mój sejf"
vaultsh vault check ./main.vault
vaultsh vault backup ./main.vault ./main.backup
vaultsh vault restore ./main.backup ./restored.vault
```

## Portfele i QR
```bash
vaultsh wallet create --vault ./main.vault --label BTC --network bitcoin
vaultsh wallet create --vault ./main.vault --label ETH --network ethereum
vaultsh wallet create --vault ./main.vault --label SOL --network solana
vaultsh wallet recover --vault ./main.vault --network ethereum
vaultsh wallet list --vault ./main.vault
vaultsh wallet recovery-phrase --vault ./main.vault --wallet-id WALLET_ID
vaultsh wallet qr --vault ./main.vault --wallet-id WALLET_ID --output ./address.png
vaultsh qr PUBLIC_ADDRESS --output ./address.png
```

## Zgoda sieciowa
W TOML ustaw `network_requests_enabled = true`; do każdej operacji dodaj jawny endpoint oraz `--config ./vaultsh.toml --allow-network`. `tor_enabled=true` blokuje żądania, bo transport Tor nie działa.

## BTC
```bash
vaultsh bitcoin balance ADDRESS --endpoint https://YOUR-ESPLORA/api --config ./vaultsh.toml --allow-network
vaultsh bitcoin history ADDRESS --endpoint https://YOUR-ESPLORA/api --config ./vaultsh.toml --allow-network --limit 10
vaultsh bitcoin send --wallet-id WALLET_ID --vault ./main.vault --to bc1qRECIPIENT --amount 0.0001 --endpoint https://YOUR-ESPLORA/api --config ./vaultsh.toml --allow-network --max-fee-sats 100000
```
**Nie używaj BTC send z prawdziwymi środkami:** kod nie odkrywa UTXO spoza pierwszego adresu odbiorczego, a reszta trafia na `/1/0`, którego nie skanuje.

## ETH i inne EVM
```bash
vaultsh ethereum balance 0xADDRESS --endpoint https://YOUR-ETH-RPC --config ./vaultsh.toml --allow-network
vaultsh ethereum send --wallet-id WALLET_ID --vault ./main.vault --to 0xRECIPIENT --amount 0.001 --endpoint https://YOUR-ETH-RPC --config ./vaultsh.toml --allow-network --max-fee-eth 0.1
vaultsh evm balance 0xADDRESS --chain polygon --endpoint https://YOUR-RPC --config ./vaultsh.toml --allow-network
```
Wysyłanie tylko natywnego ETH na Mainnet, przez legacy gasPrice. Pozostałe EVM są tylko do odczytu.

## Solana
```bash
vaultsh solana balance SOL_ADDRESS --endpoint https://YOUR-SOL-RPC --config ./vaultsh.toml --allow-network
vaultsh solana send --wallet-id WALLET_ID --vault ./main.vault --to SOL_RECIPIENT --amount 0.01 --endpoint https://YOUR-SOL-RPC --config ./vaultsh.toml --allow-network --max-fee-sol 0.01
```
Tylko natywne SOL. Podpis RPC oznacza wysłanie do endpointu, nie finalność.

## Monero (oficjalny lokalny RPC)
Zainstaluj i poprawnie skonfiguruj `monero-wallet-rpc`; port 18082 musi być wyłącznie na loopback.
```bash
vaultsh monero create-wallet MY_WALLET --config ./vaultsh.toml --allow-network
vaultsh monero open-wallet MY_WALLET --config ./vaultsh.toml --allow-network
vaultsh monero address --config ./vaultsh.toml --allow-network
vaultsh monero balance --config ./vaultsh.toml --allow-network
vaultsh monero send --to XMR_MAINNET_ADDRESS --amount 0.01 --config ./vaultsh.toml --allow-network
vaultsh monero close-wallet --config ./vaultsh.toml --allow-network
```
Pliki/seedy XMR pozostają pod kontrolą `monero-wallet-rpc`, poza sejfem Vaultsh. Nadawanie wymaga podglądu i dokładnego tekstowego potwierdzenia.
