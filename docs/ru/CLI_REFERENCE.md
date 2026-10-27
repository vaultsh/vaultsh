# Справочник командной строки (CLI)

**🌐 Язык:** [English](../CLI_REFERENCE.md) · [Polski](../pl/CLI_REFERENCE.md) · [Русский](CLI_REFERENCE.md) · [README](../../README.ru.md)

## Язык интерфейса

Опция языка указывается до команды: `vaultsh --lang ru`, `vaultsh --lang pl about` или `vaultsh --lang en networks`. Коды: `en`, `pl`, `ru`. Сейчас локализованы стартовая панель и основные информационные экраны; подробная справка подкоманд, часть запросов ввода и некоторые сообщения об ошибках пока на английском.

## Общие команды

- `vaultsh` — стартовая панель с группами команд и быстрыми шагами.
- `vaultsh version` — версия пакета.
- `vaultsh about` — статус реализации и ограничения.
- `vaultsh networks` — реализованные и планируемые сети.
- `vaultsh privacy` — настройки конфиденциальности по умолчанию.
- `vaultsh config` — настройки без секретов.

## Конфигурация

- `vaultsh config-init PATH [--force]` — создать шаблон TOML; существующий файл не заменяется без `--force`.
- `vaultsh config-check PATH` — прочитать и проверить TOML без вывода секретов.

## Хранилище

- `vaultsh vault init PATH [--label LABEL]` — создать зашифрованное хранилище; пароль вводится скрыто и подтверждается.
- `vaultsh vault check PATH` — расшифровать и проверить документ.
- `vaultsh vault backup SOURCE DESTINATION [--overwrite]` — копировать зашифрованный файл.
- `vaultsh vault restore SOURCE DESTINATION [--overwrite]` — восстановить копию; затем проверить её командой `vault check`.

## Bitcoin-кошелёк

- `vaultsh wallet create --vault PATH [--label LABEL]` — офлайн создать Mainnet-кошелёк и показать фразу восстановления.
- `vaultsh wallet recover --vault PATH [--label LABEL]` — импортировать английскую фразу BIP-39.
- `vaultsh wallet list --vault PATH` — показать публичные метаданные без фразы.
- `vaultsh wallet recovery-phrase WALLET_ID --vault PATH` — показать фразу после явного подтверждения и разблокировки хранилища.

## Bitcoin: запросы только для чтения

- `vaultsh bitcoin balance ADDRESS --endpoint URL --config PATH --allow-network` — баланс одного адреса.
- `vaultsh bitcoin history ADDRESS --endpoint URL --config PATH [--limit N] --allow-network` — первая страница истории, максимум 25 записей.

## EVM: чтение нативного баланса

- `vaultsh ethereum balance ADDRESS --endpoint URL --config PATH --allow-network` — команда для Ethereum Mainnet.
- `vaultsh evm balance ADDRESS --chain NETWORK --endpoint URL --config PATH --allow-network` — `--chain`: `ethereum`, `polygon`, `arbitrum`, `optimism`, `base`.

| Сеть | Chain ID | Актив |
|---|---:|---|
| Ethereum Mainnet | `1` | ETH |
| Polygon PoS | `137` | POL |
| Arbitrum One | `42161` | ETH |
| Optimism | `10` | ETH |
| Base | `8453` | ETH |

## Поведение и ошибки

- Публичный провайдер автоматически не выбирается.
- Для каждого сетевого запроса требуются разрешение в TOML и `--allow-network`.
- Для удалённых endpoint необходим HTTPS; HTTP разрешён только для localhost/loopback.
- Редиректы и автоматические proxy из переменных окружения отключены.
- Проверяются ответы, ID JSON-RPC, схема, числа, адреса и chain ID.
- При ожидаемой ошибке команда завершится с ненулевым кодом. Тексты ошибок не являются стабильным API pre-alpha.
- Данные провайдера не доказывают владение адресом или баланс криптографически.
