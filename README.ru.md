<div align="center">

# Vaultsh

### Мультичейн-кошелёк с самостоятельным хранением — Beta 1.0

**Локальная работа · Сеть только по явному согласию · Чёрно-оранжевый терминал**

[![Лицензия: GPL-3.0-only](https://img.shields.io/badge/License-GPL--3.0--only-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Статус](https://img.shields.io/badge/Status-Beta%201.0-orange.svg)](#статус-бета-версии-и-важные-ограничения)

</div>

**🌐 Документация / Documentation / Dokumentacja:** [English](README.md) · [Polski](README.pl.md) · [Русский](README.ru.md)

---

## Статус бета-версии и важные ограничения

**Vaultsh 1.0.0-beta.1** добавляет генерацию ключей для отдельных сетей, QR-коды публичных адресов, чтение баланса/истории и отправку нативных активов Bitcoin, Ethereum Mainnet и Solana Mainnet, а также Monero через официальный локальный процесс `monero-wallet-rpc`.

**Это бета-версия, а не кошелёк, прошедший аудит. Не храните в ней значительные средства.** В среде сборки не выполнялись запросы к реальным endpoint и не отправлялись реальные транзакции. Локальные тесты используют поддельные ответы RPC/Esplora. Перед любым использованием реальных средств установите все зависимости, запустите полный набор тестов, проверьте адреса по официальным тест-векторам, используйте одноразовые кошельки и получите независимую проверку безопасности.

## Поддерживаемые функции

| Сеть | Кошелёк/путь ключа | Чтение | Отправка | Важное ограничение |
|---|---|---|---|---|
| Bitcoin Mainnet (BTC) | Английская BIP-39; BIP-84 `m/84'/0'/0'/0/0` | Баланс и первая страница истории одного адреса | Локальная подпись P2WPKH и отправка через Esplora после точного подтверждения | Выбор UTXO включает только подтверждённые UTXO первого адреса получения. Нет поиска всех адресов, агрегации всего кошелька и поиска сдачи. Сдача отправляется на путь `/1/0`, который эта версия не сканирует. |
| Ethereum Mainnet (ETH) | BIP-39; BIP-44 `m/44'/60'/0'/0/0` | Баланс нативного ETH | Локально подписанная нативная ETH-транзакция, legacy EIP-155 | Отправка только нативного ETH с chain ID 1. Нет ERC-20, контрактов, EIP-1559, multisig, аппаратных кошельков и отслеживания подтверждений. |
| Остальные профили EVM | Можно запрашивать баланс того же формата публичного адреса | Нативный баланс Polygon PoS, Arbitrum One, Optimism и Base с проверкой chain ID | Отправка отключена | Эти профили доступны только для чтения. `evm balance` не означает поддержку EVM-транзакций. |
| Solana Mainnet Beta (SOL) | Английская BIP-39; `m/44'/501'/0'/0'` через `bip-utils` и `solders` | Баланс нативного SOL | Локально подписанный перевод SOL, явная отправка RPC | Нет токенов SPL, поиска адресов, истории и проверки finality. Ответ RPC о принятии запроса не гарантирует подтверждение. |
| Monero Mainnet (XMR) | Официальные файлы кошелька и ключи через локальный `monero-wallet-rpc` | Основной адрес и баланс кошелька | `transfer` с `do_not_relay`, просмотр, затем `relay_tx` после подтверждения | Seed и файлы `.keys` Monero хранятся вне зашифрованного хранилища Vaultsh. Настройка RPC/узла и синхронизация — ответственность пользователя. |

Кошельки BTC/ETH/SOL хранят фразу BIP-39 внутри аутентифицированного зашифрованного файла Vaultsh. Monero использует собственный формат и **не хранится в этом хранилище**. Обычный список кошельков не показывает фразы. После создания кошелька обязательно сохраните фразу офлайн.

## Возможности

- Полноэкранный Textual-интерфейс в чёрно-оранжевой гамме: вкладки, таблицы, формы, навигация по файлам, заголовок и подвал; запасная панель Rich.
- Документация на английском, польском и русском; основные элементы интерфейса поддерживают `--lang en|pl|ru`.
- Локальные зашифрованные хранилища, аутентифицированное шифрование, резервное копирование/восстановление и записи BTC/ETH/SOL в схеме v3.
- Создание и восстановление кошельков BIP-39 BTC, ETH и SOL.
- Показ QR и сохранение PNG для распознаваемых форматов публичных адресов BTC/EVM/XMR/SOL. QR отклоняет пробелы/фразы восстановления и строки, похожие на необработанные приватные ключи. Распознавание формата не заменяет проверку адреса на экране.
- Явно указанные HTTPS-endpoint Esplora/JSON-RPC; сетевые клиенты блокируют перенаправления и не используют системные proxy-переменные.
- Двойное разрешение сети: `network_requests_enabled = true` **и** `--allow-network`.
- Точное преобразование десятичных сумм в базовые единицы без чисел с плавающей точкой.
- Предпросмотр транзакции (сумма, адрес, комиссия) и точное текстовое подтверждение. Нет `--yes`, обходящего подтверждение.
- Интеграция Monero ограничена локальным `monero-wallet-rpc`; удалённые endpoint wallet-RPC отклоняются.

## Установка

Требуется Python 3.12 или новее. В корне проекта:

```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# Linux / macOS / Termux: source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Если pip не может подключиться к PyPI, установка не завершена. Проект требует зависимости из `pyproject.toml`, включая `embit`, `eth-account`, `bip-utils`, `solders`, `qrcode[pil]`, `textual` и тестовые инструменты. Пропущенный тест не означает, что функция проверена.

## Первый запуск

```bash
vaultsh --lang ru               # либо --lang en / --lang pl
vaultsh --help
vaultsh version
vaultsh networks
vaultsh config-init ./vaultsh.toml
vaultsh config-check ./vaultsh.toml
```

Созданная конфигурация по умолчанию запрещает сеть. Изменяйте `vaultsh.toml`, только если собираетесь выполнять запросы:

```toml
[app]
app_name = "vaultsh"
telemetry_enabled = false
network_requests_enabled = true
tor_enabled = false
request_timeout_seconds = 15.0
```

`network_requests_enabled = true` разрешает сетевые команды, но каждая команда всё равно требует `--allow-network`. Оставляйте `tor_enabled = false`: Vaultsh не реализует транспорт Tor, и при его включении сетевые команды отказываются от соединения. Endpoint может видеть запрошенные адреса и метаданные соединения.

## Создание хранилища и кошельков

```bash
vaultsh vault init ./main.vault --label "Main Vault"
vaultsh wallet create --vault ./main.vault --label "BTC savings" --network bitcoin
vaultsh wallet create --vault ./main.vault --label "ETH account" --network ethereum
vaultsh wallet create --vault ./main.vault --label "SOL account" --network solana
vaultsh wallet list --vault ./main.vault
```

Для импорта английской фразы BIP-39 из 12 или 24 слов используйте `vaultsh wallet recover --vault ./main.vault --network ethereum` (или `bitcoin` / `solana`). В этой бета-версии поддерживается только пустая дополнительная BIP-39 passphrase. Для отправки нужны ID кошелька и файл хранилища.

**Защищайте фразу восстановления и пароль хранилища отдельно.** Любой, кто знает фразу, может управлять соответствующим кошельком. Не вставляйте её в issues, чат, историю shell, облачные заметки или скриншоты. Зашифрованное хранилище не защищает фразу после её отображения или копирования за его пределы.

## QR-коды адресов получения

Показать QR для кошелька в хранилище:

```bash
vaultsh wallet qr WALLET_ID --vault ./main.vault
vaultsh wallet qr WALLET_ID --vault ./main.vault --output ./receive-address.png
```

Или создать QR по публичному адресу:

```bash
vaultsh qr bc1qPUBLIC_ADDRESS
vaultsh qr 0x40_HEX_ADDRESS --output ./eth-address.png
```

QR содержит только публичный адрес, а не платёжный запрос с суммой. Проверка формата не является полной проверкой контрольной суммы каждого типа адреса. До передачи адреса проверьте его после декодирования QR.

## Сеть и отправка

Все команды ниже требуют `network_requests_enabled = true`, явно выбранный endpoint и `--allow-network`. Используйте доверенные endpoint; не публикуйте URL, содержащие access-token.

### Bitcoin Mainnet

```bash
vaultsh bitcoin balance ADDRESS --endpoint https://YOUR-ESPLORA/api --config ./vaultsh.toml --allow-network
vaultsh bitcoin history ADDRESS --endpoint https://YOUR-ESPLORA/api --config ./vaultsh.toml --allow-network --limit 10
vaultsh bitcoin send --wallet-id WALLET_ID --vault ./main.vault --to bc1qRECIPIENT --amount 0.0001 --endpoint https://YOUR-ESPLORA/api --config ./vaultsh.toml --allow-network --max-fee-sats 100000
```

Отправка BTC использует только подтверждённые UTXO первого адреса получения. Адреса с другими индексами и ветка сдачи не сканируются. Баланс одного адреса — это не полный баланс кошелька.

### Ethereum Mainnet

```bash
vaultsh ethereum balance 0xYOUR_40_HEX_ADDRESS --endpoint https://YOUR-ETH-RPC --config ./vaultsh.toml --allow-network
vaultsh ethereum send --wallet-id WALLET_ID --vault ./main.vault --to 0xRECIPIENT --amount 0.001 --endpoint https://YOUR-ETH-RPC --config ./vaultsh.toml --allow-network --max-fee-eth 0.1
```

Отправка включена только для нативного ETH с chain ID `1`. Чтение EVM-баланса также поддерживает Polygon PoS (`137`), Arbitrum One (`42161`), Optimism (`10`) и Base (`8453`), но отправка в них отключена. Сейчас используется legacy-транзакция с `gasPrice`, не EIP-1559.

### Solana Mainnet Beta

```bash
vaultsh solana balance SOL_PUBLIC_ADDRESS --endpoint https://YOUR-SOLANA-RPC --config ./vaultsh.toml --allow-network
vaultsh solana send --wallet-id WALLET_ID --vault ./main.vault --to SOL_RECIPIENT --amount 0.01 --endpoint https://YOUR-SOLANA-RPC --config ./vaultsh.toml --allow-network --max-fee-sol 0.01
```

Клиент проверяет genesis hash Solana Mainnet, локально создаёт и подписывает нативный перевод SOL и отправляет его только после подтверждения. Ответ `sendTransaction` говорит о принятии запроса RPC, но не гарантирует финальность.

### Monero Mainnet

Vaultsh не реализует собственный код ключей/seed Monero. Установите Monero из официального проекта и запустите локально `monero-wallet-rpc` рядом с синхронизированным `monerod` или намеренно выбранным узлом. Пример (адаптируйте пути и пароль):

```bash
monero-wallet-rpc --rpc-bind-ip 127.0.0.1 --rpc-bind-port 18082 \\
  --wallet-dir ./monero-wallets \\
  --rpc-login vaultshrpc:REPLACE_WITH_LONG_RPC_PASSWORD \\
  --daemon-address http://127.0.0.1:18081
```

Предполагается, что `monerod` доступен по `127.0.0.1:18081`. Не открывайте wallet-RPC на публичном интерфейсе.

```bash
vaultsh monero create-wallet savings --rpc-username vaultshrpc --config ./vaultsh.toml --allow-network
vaultsh monero address --rpc-username vaultshrpc --config ./vaultsh.toml --allow-network
vaultsh monero balance --rpc-username vaultshrpc --config ./vaultsh.toml --allow-network
vaultsh monero send --to XMR_MAINNET_RECIPIENT --amount 0.01 --rpc-username vaultshrpc --config ./vaultsh.toml --allow-network
```

Vaultsh скрывает ввод RPC-пароля и пароля кошелька. `monero-wallet-rpc` управляет XMR-кошельком и файлами ключей в собственном каталоге вне хранилища Vaultsh. Защитите резервную копию кошелька Monero и seed. Конфигурация демона определяет используемый узел; Vaultsh проверяет адрес Mainnet, но не управляет демоном и не проводит его аудит.

## Безопасность транзакций

- Программа подготавливает и локально подписывает BTC/ETH/SOL или просит `monero-wallet-rpc` подготовить XMR-транзакцию без отправки.
- Отображаются адрес, сумма, комиссия и сведения о сети; затем требуется точная фраза подтверждения. Нет флага `--yes`, отключающего подтверждение.
- Подписанную транзакцию может отправить любой, кто получит её до relay. Не сохраняйте её в логах и не отправляйте в чат. Скрытие данных из `repr` не гарантирует очистку памяти Python.
- Ответ endpoint может быть ложным или устаревшим. Хеш/подпись часто означает принятие отправки, а не подтверждение транзакции.
- Тестируйте на одноразовом кошельке и с минимальными суммами. Модульные тесты не доказывают безопасность реальных операций.

## Тесты и разработка

```bash
python -m compileall -q src tests
python -m pytest --cov=vaultsh --cov-report=term-missing -q
ruff check .
mypy src/vaultsh
```

Некоторым тестам требуются все зависимости и отдельная проверка с контролируемыми узлами. Модульные тесты используют фиктивные ответы и не отправляют транзакции. См. [отчёт тестов](docs/TEST_RESULTS.md), [модель безопасности](docs/SECURITY_MODEL.md) и [сетевые адаптеры](docs/NETWORK_ADAPTERS.md).

## Ещё не реализовано

- Независимый аудит безопасности и подтверждённый процесс выпуска.
- Сканирование адресов всего кошелька/gap limit; баланс и расход BTC ограничены первым адресом, ветка сдачи не сканируется.
- ERC-20, вызовы контрактов, EVM-подпись за пределами Ethereum Mainnet, EIP-1559 и мониторинг receipt/finality.
- SPL-токены, история транзакций и проверка подтверждений Solana.
- Файлы Monero не импортируются и не шифруются хранилищем Vaultsh; восстановление и резервные копии выполняются средствами Monero.
- Нет транспорта Tor, аппаратных кошельков, multisig, интерфейса cold signing и полного тестирования с реальными узлами.
- Textual UI пока предоставляет базовые операции хранилища/кошельков и формы чтения; отправка выполняется командами CLI выше.

## Лицензия

Vaultsh распространяется по лицензии `GPL-3.0-only`. См. [LICENSE](LICENSE).
