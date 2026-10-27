# Архитектура — Vaultsh 1.0.0-beta.1

- `cli.py`: Typer-команды, проверки ввода, обзор операции, точное подтверждение перед broadcast/relay.
- `ui/`: Textual, Rich fallback, EN/PL/RU, QR/prompt.
- `crypto/`: Scrypt + AES-256-GCM и инструменты derivation.
- `storage/`: формат хранилища, зашифрованные записи, backup/restore.
- `networks/bitcoin/`: BIP84, Esplora, ограниченный UTXO selection, локальная P2WPKH-подпись и broadcast.
- `networks/ethereum/`: JSON-RPC и локальная подпись legacy EIP-155 только для ETH Mainnet.
- `networks/solana/`: RPC Mainnet, нативный SOL, библиотека `solders`.
- `networks/monero/`: loopback-клиент официального `monero-wallet-rpc`; XMR keys/seed и подпись принадлежат этому процессу.
- `privacy/network_policy.py`: разрешение TOML плюс `--allow-network`; Tor не реализован.

BTC/ETH/SOL: загрузка записи из сейфа, запрос к выбранному endpoint, локальная сборка/подпись, показ сети/адреса/суммы/комиссии и точное подтверждение, затем отправка. XMR: RPC подготавливает транзакцию без relay; после подтверждения Vaultsh передаёт метаданные `relay_tx`.

**Критическое ограничение BTC:** поиск UTXO охватывает только подтверждённые UTXO первого receive-адреса. Сдача отправляется на `/1/0`, который Vaultsh не сканирует. Не отправляйте реальные BTC.
