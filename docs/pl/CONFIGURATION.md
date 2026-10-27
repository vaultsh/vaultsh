# Konfiguracja

**🌐 Język:** [English](../CONFIGURATION.md) · [Polski](CONFIGURATION.md) · [Русский](../ru/CONFIGURATION.md) · [README](../../README.pl.md)

## Utworzenie i walidacja konfiguracji

```bash
vaultsh config-init ./vaultsh.toml
vaultsh config-check ./vaultsh.toml
```

Przykładowy plik:

```toml
[app]
app_name = "vaultsh"
telemetry_enabled = false
network_requests_enabled = false
tor_enabled = false
request_timeout_seconds = 15.0
```

## Ustawienia

| Klucz | Typ | Domyślnie | Znaczenie |
|---|---|---|---|
| `app_name` | tekst | `"vaultsh"` | Niepusta, przycięta nazwa aplikacji. |
| `telemetry_enabled` | bool | `false` | Telemetria jest wyłączona; aplikacja nie ma nadawcy analityki. |
| `network_requests_enabled` | bool | `false` | Zgoda konfiguracyjna na zapytania Bitcoin/EVM tylko do odczytu. |
| `tor_enabled` | bool | `false` | Gdy `true`, polecenia sieciowe odmawiają bezpośredniego połączenia, bo transport Tor nie działa. |
| `request_timeout_seconds` | liczba | `15.0` | Timeout pojedynczego zapytania; dozwolony zakres 0.1–300 sekund. |

## Podwójna zgoda na sieć

Aby wykonać zapytanie, muszą jednocześnie wystąpić dwa warunki: `network_requests_enabled = true` w pliku wybranym przez `--config` oraz flaga `--allow-network`. Brak któregokolwiek z nich blokuje połączenie. Samo ustawienie `tor_enabled` nie uruchamia Tor.

## Reguły endpointów i prywatność

Zdalne endpointy muszą używać HTTPS. Zwykłe HTTP jest dostępne wyłącznie dla localhost lub adresów loopback, np. lokalnego węzła. Odrzucane są dane logowania w URL, query string, fragmenty, znaki kontrolne i segmenty ścieżki `.`/`..`. Przekierowania nie są śledzone, a proxy z otoczenia nie są automatycznie używane. Endpoint jest podawany przy każdym poleceniu i nie jest zapisywany w `AppConfig`.

Endpoint otrzymuje sprawdzany publiczny adres i może powiązać go z metadanymi połączenia. Tor nie jest obsługiwany. Niektóre RPC umieszczają token w ścieżce URL — traktuj go jak sekret i nie publikuj w zgłoszeniach, logach ani zrzutach ekranu.
