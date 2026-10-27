# Конфигурация

**🌐 Язык:** [English](../CONFIGURATION.md) · [Polski](../pl/CONFIGURATION.md) · [Русский](CONFIGURATION.md) · [README](../../README.ru.md)

## Создание и проверка файла

```bash
vaultsh config-init ./vaultsh.toml
vaultsh config-check ./vaultsh.toml
```

Пример:

```toml
[app]
app_name = "vaultsh"
telemetry_enabled = false
network_requests_enabled = false
tor_enabled = false
request_timeout_seconds = 15.0
```

## Параметры

| Ключ | Тип | По умолчанию | Назначение |
|---|---|---|---|
| `app_name` | строка | `"vaultsh"` | Непустое название приложения без пробелов по краям. |
| `telemetry_enabled` | bool | `false` | Телеметрия выключена; отправителя аналитики в приложении нет. |
| `network_requests_enabled` | bool | `false` | Разрешение конфигурации на read-only запросы Bitcoin/EVM. |
| `tor_enabled` | bool | `false` | Если `true`, сетевые команды отказываются от прямого соединения, так как транспорт Tor не реализован. |
| `request_timeout_seconds` | число | `15.0` | Тайм-аут одного запроса, допустимы 0.1–300 секунд. |

## Двойное разрешение сети

Нужны оба условия: `network_requests_enabled = true` в TOML, указанном через `--config`, и флаг `--allow-network`. При отсутствии любого условия запрос блокируется. `tor_enabled` сам по себе не запускает Tor.

## Endpoint и конфиденциальность

Для удалённых endpoint обязателен HTTPS. HTTP разрешён только для localhost/loopback, например локального узла. URL с встроенными учётными данными, query string, fragment, управляющими символами и сегментами пути `.`/`..` отклоняются. Перенаправления не отслеживаются, proxy из окружения автоматически не используются. Адрес endpoint передаётся каждой команде и не сохраняется в `AppConfig`.

Endpoint получает проверяемый публичный адрес и может связать его с метаданными соединения. Tor не поддерживается. Некоторые RPC-провайдеры включают токен в путь URL — рассматривайте его как секрет и не публикуйте в issue, логах или скриншотах.
