<div align="center">

# Vaultsh

### Self-custody multi-chain wallet — Beta 1.0

**Local-first · Explicit network consent · Black & orange terminal UI**

[![License: GPL-3.0-only](https://img.shields.io/badge/License-GPL--3.0--only-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Beta%201.0-orange.svg)](#beta-status-and-important-limitations)

</div>

**🌐 Documentation / Dokumentacja / Документация:** [English](README.md) · [Polski](README.pl.md) · [Русский](README.ru.md)

---

## Beta status and important limitations

Vaultsh **1.0.0-beta.1** adds chain-specific wallet derivation, QR codes for public addresses, read-only balance/history queries, and opt-in native-asset transfer workflows for Bitcoin, Ethereum Mainnet, Solana Mainnet, and Monero via the official local `monero-wallet-rpc` process.

**This is a beta, not an audited wallet. Do not use it to store significant funds.** The code in this release has not been tested against real endpoints or used to broadcast real transactions in the build environment. Local tests use mocked RPC/Esplora responses. Before considering any real-money use, install all dependencies, run all tests, verify wallet addresses against official vectors, test with disposable wallets, and get an independent security review.

## Supported functionality

| Chain | Wallet/key path | Read operations | Send capability | Important limitation |
|---|---|---|---|---|
| Bitcoin Mainnet (BTC) | English BIP-39; BIP-84 `m/84'/0'/0'/0/0` | Balance and first page of history for one address | Local P2WPKH signing and Esplora broadcast after typed confirmation | Spend selection scans confirmed UTXOs only at the first receive address. Address discovery, wallet-wide aggregation and change discovery are not implemented. Change uses BIP-84 branch `/1/0`, which this release does not scan. |
| Ethereum Mainnet (ETH) | BIP-39; BIP-44 `m/44'/60'/0'/0/0` | Native ETH balance | Locally signed native ETH transfer, legacy EIP-155 transaction | Only native ETH on chain ID 1 is sendable. No ERC-20, contract calls, EIP-1559 fee market, multisig, hardware wallet, or full nonce/receipt tracking. |
| Other listed EVM mainnets | Same public-address format may be queried | Native balance on Polygon PoS, Arbitrum One, Optimism and Base, with chain-ID check | Not enabled for sending | These profiles are read-only. `evm balance` does not imply EVM transaction support. |
| Solana Mainnet Beta (SOL) | English BIP-39; `m/44'/501'/0'/0'` via `bip-utils` + `solders` | Native SOL balance | Locally signed native SOL transfer; explicit RPC submission | SPL tokens, address discovery, transaction history and finality polling are not implemented. RPC submission is not proof of confirmation. |
| Monero Mainnet (XMR) | Official Monero wallet files and key handling via local `monero-wallet-rpc` | Primary address and wallet balance | `transfer` with `do_not_relay`, preview, then `relay_tx` after typed confirmation | Monero seed and `.keys` files are managed by Monero RPC outside the Vaultsh encrypted vault. RPC daemon/node setup and synchronization are the user's responsibility. |

Wallet data for BTC/ETH/SOL stores the BIP-39 phrase inside the authenticated encrypted Vaultsh file. Monero uses its own wallet format and is **not** stored in that vault. Recovery phrases are not displayed in ordinary wallet lists. The phrase shown at creation must be backed up offline.

## Features

- Textual full-screen terminal interface with black/orange styling, tabs, tables, forms, directory browsing, header and footer; Rich dashboard fallback.
- English, Polish and Russian documentation and major UI labels (`--lang en|pl|ru`).
- Encrypted local vault documents, password-based authenticated encryption, backup/restore, and schema-v3 wallet records for BTC/ETH/SOL.
- Wallet creation/recovery for BIP-39 BTC, ETH and SOL profiles.
- QR display and PNG export for recognizable public BTC/EVM/XMR/SOL address formats. QR input rejects whitespace/recovery phrases and raw private-key-like hex strings. Format recognition is not a substitute for checking the destination on screen.
- Explicitly chosen HTTPS endpoints for Esplora and JSON-RPC; redirects and ambient proxies are disabled by the network clients.
- Two-part network permission: saved `network_requests_enabled = true` **and** command-line `--allow-network`.
- Exact decimal-to-base-unit conversion; no floating-point amount conversion.
- Transfer preview with amount, destination, fee estimate/cap and network details, followed by an exact typed confirmation. There is no `--yes` bypass.
- Monero integration is restricted to loopback `monero-wallet-rpc`; remote wallet-RPC endpoints are refused.

## Install

Use Python 3.12 or newer. From the project root:

```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# Linux / macOS / Termux: source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

If pip cannot reach PyPI, installation is incomplete; the project requires the dependencies declared in `pyproject.toml`, including `embit`, `eth-account`, `bip-utils`, `solders`, `qrcode[pil]`, `textual`, and the test tools. Do not assume a skipped test means a feature is verified.

## First run

```bash
vaultsh --lang pl                 # or --lang en / --lang ru
vaultsh --help
vaultsh version
vaultsh networks
vaultsh config-init ./vaultsh.toml
vaultsh config-check ./vaultsh.toml
```

Network access is disabled in the generated config. Edit `vaultsh.toml` only when you are ready to make a request:

```toml
[app]
app_name = "vaultsh"
telemetry_enabled = false
network_requests_enabled = true
tor_enabled = false
request_timeout_seconds = 15.0
```

Setting `network_requests_enabled = true` permits network commands, but each command still requires `--allow-network`. `tor_enabled` must remain `false` because Vaultsh does not implement Tor transport; if enabled, the network command refuses to proceed. The clients do not route automatically through a proxy. An endpoint can see queried public addresses and connection metadata.

## Create a vault and wallet

```bash
vaultsh vault init ./main.vault --label "Main Vault"
vaultsh wallet create --vault ./main.vault --label "BTC savings" --network bitcoin
vaultsh wallet create --vault ./main.vault --label "ETH account" --network ethereum
vaultsh wallet create --vault ./main.vault --label "SOL account" --network solana
vaultsh wallet list --vault ./main.vault
```

Use `vaultsh wallet recover --vault ./main.vault --network ethereum` (or `bitcoin` / `solana`) to import an English 12- or 24-word BIP-39 phrase. This beta uses the empty BIP-39 passphrase only. Wallet IDs are shown by `wallet list`; send commands require the correct wallet ID and vault file.

**Protect the seed phrase and vault password separately.** Anyone who obtains a seed phrase can control the associated wallet. Do not paste it into issues, chat, shell history, cloud notes or screenshots. A password-protected vault does not protect a phrase after it has been displayed or copied elsewhere.

## QR codes for receive addresses

Show a wallet's QR from the encrypted vault:

```bash
vaultsh wallet qr WALLET_ID --vault ./main.vault
vaultsh wallet qr WALLET_ID --vault ./main.vault --output ./receive-address.png
```

Or render/save a recognized public address directly:

```bash
vaultsh qr bc1qYOURPUBLICADDRESS
vaultsh qr 0xYOUR_40_HEX_ADDRESS --output ./eth-address.png
```

QR contains the public address only. It is not a payment request with an amount, and the QR helper's format check is not a full chain-specific checksum verifier for every address type. Check the decoded address against the one shown by your wallet before sharing it.

## Network and send commands

All examples below require `network_requests_enabled = true`, an explicit endpoint, and `--allow-network`. Use endpoints you trust; never paste access-token URLs into screenshots or public issues.

### Bitcoin Mainnet

```bash
vaultsh bitcoin balance ADDRESS --endpoint https://YOUR-ESPLORA/api --config ./vaultsh.toml --allow-network
vaultsh bitcoin history ADDRESS --endpoint https://YOUR-ESPLORA/api --config ./vaultsh.toml --allow-network --limit 10
vaultsh bitcoin send --wallet-id WALLET_ID --vault ./main.vault --to bc1qRECIPIENT --amount 0.0001 --endpoint https://YOUR-ESPLORA/api --config ./vaultsh.toml --allow-network --max-fee-sats 100000
```

BTC send is limited to confirmed UTXOs at the wallet's first receive address. It does not scan address indexes or spend UTXOs on its change branch. Do not mistake one-address balance/history for the complete wallet balance.

### Ethereum Mainnet

```bash
vaultsh ethereum balance 0xYOUR_40_HEX_ADDRESS --endpoint https://YOUR-ETH-RPC --config ./vaultsh.toml --allow-network
vaultsh ethereum send --wallet-id WALLET_ID --vault ./main.vault --to 0xRECIPIENT --amount 0.001 --endpoint https://YOUR-ETH-RPC --config ./vaultsh.toml --allow-network --max-fee-eth 0.1
```

Only native ETH sends on chain ID `1` are enabled. EVM balance queries also support Polygon PoS (`137`), Arbitrum One (`42161`), Optimism (`10`) and Base (`8453`), but sending on those profiles is disabled. The current transfer path uses a legacy `gasPrice` transaction, not an EIP-1559 transaction.

### Solana Mainnet Beta

```bash
vaultsh solana balance SOL_PUBLIC_ADDRESS --endpoint https://YOUR-SOLANA-RPC --config ./vaultsh.toml --allow-network
vaultsh solana send --wallet-id WALLET_ID --vault ./main.vault --to SOL_RECIPIENT --amount 0.01 --endpoint https://YOUR-SOLANA-RPC --config ./vaultsh.toml --allow-network --max-fee-sol 0.01
```

The client checks the endpoint's Solana Mainnet genesis hash, creates and signs a native SOL transfer locally, and submits it only after the confirmation phrase. The `sendTransaction` response is a signature/submission acknowledgement, not a confirmation/finality guarantee.

### Monero Mainnet

Vaultsh does not implement Monero seed/key code. Install Monero from the official project and run `monero-wallet-rpc` locally alongside a synchronized `monerod` or a node you deliberately selected. For example, create a wallet directory and run wallet RPC bound only to loopback (adjust paths and credentials for your system):

```bash
monero-wallet-rpc --rpc-bind-ip 127.0.0.1 --rpc-bind-port 18082 \\
  --wallet-dir ./monero-wallets \\
  --rpc-login vaultshrpc:REPLACE_WITH_A_LONG_RPC_PASSWORD \\
  --daemon-address http://127.0.0.1:18081
```

This assumes `monerod` is available at `127.0.0.1:18081`. Do not bind wallet RPC to a public interface. Then use:

```bash
vaultsh monero create-wallet savings --rpc-username vaultshrpc --config ./vaultsh.toml --allow-network
vaultsh monero address --rpc-username vaultshrpc --config ./vaultsh.toml --allow-network
vaultsh monero balance --rpc-username vaultshrpc --config ./vaultsh.toml --allow-network
vaultsh monero send --to XMR_MAINNET_RECIPIENT --amount 0.01 --rpc-username vaultshrpc --config ./vaultsh.toml --allow-network
```

Vaultsh prompts for RPC authentication and wallet passwords without echo. `monero-wallet-rpc` manages the XMR wallet and key files in its configured wallet directory, outside the Vaultsh vault. Back up that Monero wallet and its seed securely. The daemon endpoint determines which node and network your wallet actually uses; Vaultsh validates the returned address as Mainnet, but does not manage or audit the Monero daemon.

## Transaction safety

- The send workflow prepares and locally signs BTC/ETH/SOL transactions or asks `monero-wallet-rpc` to create a non-relayed XMR transaction.
- It displays destination, amount, fee and other network-specific information, then requires the user to type the exact confirmation phrase. No `--yes`/skip-confirmation option is provided.
- A signed transaction is a bearer object: anyone who obtains it before relay may broadcast it. Keep it out of logs and chat. The preview objects hide signed bytes/metadata from their `repr`, but this is not a guarantee that Python memory is wiped.
- Endpoint responses may be dishonest or stale. A returned transaction hash/signature normally means the provider accepted the submission, not that the transaction is confirmed.
- Use a fresh disposable wallet and tiny amounts for beta validation. Do not treat successful unit tests as evidence that the network workflow is safe for real funds.

## Test and develop

```bash
python -m compileall -q src tests
python -m pytest --cov=vaultsh --cov-report=term-missing -q
ruff check .
mypy src/vaultsh
```

Some integration tests require all runtime dependencies and a separate online/controlled-node test setup. Unit tests in this repo mock network responses and do not broadcast transactions. See [test results](docs/TEST_RESULTS.md), [security model](docs/SECURITY_MODEL.md), and [network adapter details](docs/NETWORK_ADAPTERS.md).

## Important missing features

- No independent security audit or verified release pipeline.
- No wallet-wide address discovery/gap-limit scan; BTC balance/UTXO spend is scoped to the first receive address and change outputs are not scanned.
- No ERC-20 tokens, contract interactions, EVM signing outside Ethereum Mainnet, EIP-1559, or transaction receipt/finality polling.
- No Solana SPL tokens, transaction history or confirmation polling.
- Monero wallet files are not imported into or encrypted by Vaultsh's vault; Monero seed recovery and backup use official Monero wallet tooling.
- No Tor transport, hardware wallet, multisig, cold-signing UI or reliable integration testing against real nodes.
- The Textual UI currently exposes vault/wallet basics and read-only query forms; sending is done through the CLI commands listed above.

## License

Vaultsh is distributed under `GPL-3.0-only`. See [LICENSE](LICENSE).
