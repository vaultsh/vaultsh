# Konfiguracja — Vaultsh 1.0.0-beta.1

`vaultsh config-init ./vaultsh.toml` tworzy konfigurację bez sekretów, a `vaultsh config-check ./vaultsh.toml` sprawdza jej poprawność. Nie zapisuj tu haseł, fraz odzyskiwania, kluczy prywatnych, tokenów API ani haseł Monero RPC.

```toml
[app]
app_name = "vaultsh"
telemetry_enabled = false
network_requests_enabled = false
tor_enabled = false
request_timeout_seconds = 15.0
```

| Ustawienie | Domyślnie | Znaczenie |
|---|---|---|
| `app_name` | `vaultsh` | Nazwa wyświetlana/metadane |
| `telemetry_enabled` | `false` | Telemetria nie jest zaimplementowana |
| `network_requests_enabled` | `false` | Zezwolenie na endpointy i lokalne Monero RPC |
| `tor_enabled` | `false` | Transport Tor nie istnieje; `true` blokuje operacje sieciowe |
| `request_timeout_seconds` | `15.0` | Timeout 0,1–300 s |

Każde połączenie wymaga ustawienia `network_requests_enabled = true` i flagi `--allow-network`; endpoint podawany jest jawnie. Dostawca może zobaczyć publiczny adres i metadane sieciowe. XMR RPC domyślnie używa `http://127.0.0.1:18082/json_rpc` i klient odrzuca URL-e nie-loopback. Nie wystawiaj RPC na interfejs publiczny.
