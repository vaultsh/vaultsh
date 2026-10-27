# Конфигурация — Vaultsh 1.0.0-beta.1

`vaultsh config-init ./vaultsh.toml` создаёт конфигурацию без секретов, а `vaultsh config-check ./vaultsh.toml` проверяет её. Не записывайте здесь пароли, seed-фразы, приватные ключи, API-токены или пароли Monero RPC.

```toml
[app]
app_name = "vaultsh"
telemetry_enabled = false
network_requests_enabled = false
tor_enabled = false
request_timeout_seconds = 15.0
```

| Параметр | По умолчанию | Назначение |
|---|---|---|
| `app_name` | `vaultsh` | Имя для отображения/метаданных |
| `telemetry_enabled` | `false` | Телеметрия не реализована |
| `network_requests_enabled` | `false` | Разрешение для endpoint и локального Monero RPC |
| `tor_enabled` | `false` | Транспорт Tor отсутствует; `true` блокирует сетевые операции |
| `request_timeout_seconds` | `15.0` | Тайм-аут 0,1–300 секунд |

Для каждого сетевого действия требуется `network_requests_enabled = true` и флаг `--allow-network`; endpoint указывается явно. Провайдер может видеть публичный адрес и метаданные соединения. XMR RPC по умолчанию использует `http://127.0.0.1:18082/json_rpc`, клиент отклоняет не-loopback URL. Не открывайте RPC в публичную сеть.
