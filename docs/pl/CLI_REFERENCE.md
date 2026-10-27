# Referencja wiersza poleceń (CLI)

**🌐 Język:** [English](../CLI_REFERENCE.md) · [Polski](CLI_REFERENCE.md) · [Русский](../ru/CLI_REFERENCE.md) · [README](../../README.pl.md)

## Język interfejsu

Opcję języka umieść przed poleceniem: `vaultsh --lang pl`, `vaultsh --lang ru about` albo `vaultsh --lang en networks`. Dostępne kody: `en`, `pl`, `ru`. W bieżącej wersji tłumaczone są ekran startowy i główne ekrany informacyjne. Szczegółowa pomoc podkomend, część promptów i niektóre błędy nadal są po angielsku.

## Polecenia ogólne

- `vaultsh` — panel startowy z grupami poleceń i szybkim startem.
- `vaultsh version` — wersja pakietu.
- `vaultsh about` — zakres implementacji i ograniczenia.
- `vaultsh networks` — obsługiwane oraz planowane sieci.
- `vaultsh privacy` — domyślne ustawienia prywatności.
- `vaultsh config` — domyślne ustawienia bez sekretów.

## Konfiguracja

- `vaultsh config-init PATH [--force]` — utwórz niesekretny szablon TOML; bez `--force` istniejący plik nie jest nadpisywany.
- `vaultsh config-check PATH` — wczytaj i zweryfikuj TOML bez wyświetlania sekretów.

## Sejf

- `vaultsh vault init PATH [--label LABEL]` — utwórz nowy zaszyfrowany sejf; hasło jest ukryte i wymaga potwierdzenia.
- `vaultsh vault check PATH` — odszyfruj i sprawdź dokument sejfu.
- `vaultsh vault backup SOURCE DESTINATION [--overwrite]` — skopiuj zaszyfrowany plik.
- `vaultsh vault restore SOURCE DESTINATION [--overwrite]` — odtwórz kopię; potem użyj `vault check`, aby zweryfikować hasło.

## Portfel Bitcoin

- `vaultsh wallet create --vault PATH [--label LABEL]` — utwórz portfel Mainnet offline i pokaż frazę odzyskiwania.
- `vaultsh wallet recover --vault PATH [--label LABEL]` — importuj angielską frazę BIP-39.
- `vaultsh wallet list --vault PATH` — pokaż publiczne metadane bez frazy.
- `vaultsh wallet recovery-phrase WALLET_ID --vault PATH` — pokaż frazę po jawnym potwierdzeniu i odblokowaniu sejfu.

## Zapytania Bitcoin tylko do odczytu

- `vaultsh bitcoin balance ADDRESS --endpoint URL --config PATH --allow-network` — saldo jednego adresu.
- `vaultsh bitcoin history ADDRESS --endpoint URL --config PATH [--limit N] --allow-network` — pierwsza strona historii adresu, maksymalnie 25 rekordów.

## Zapytania salda EVM tylko do odczytu

- `vaultsh ethereum balance ADDRESS --endpoint URL --config PATH --allow-network` — skrót dla Ethereum Mainnet.
- `vaultsh evm balance ADDRESS --chain NETWORK --endpoint URL --config PATH --allow-network` — obsługiwane wartości `--chain`: `ethereum`, `polygon`, `arbitrum`, `optimism`, `base`.

| Sieć | Chain ID | Aktywo |
|---|---:|---|
| Ethereum Mainnet | `1` | ETH |
| Polygon PoS | `137` | POL |
| Arbitrum One | `42161` | ETH |
| Optimism | `10` | ETH |
| Base | `8453` | ETH |

## Zachowanie operacyjne

- Program nie wybiera automatycznie publicznego dostawcy.
- Każde zapytanie wymaga zgody w TOML oraz `--allow-network`.
- Zdalny endpoint musi używać HTTPS; HTTP jest dopuszczony jedynie dla localhost/loopback.
- Przekierowania i proxy z automatycznych zmiennych środowiskowych są wyłączone.
- Odpowiedzi, ID JSON-RPC, schematy, ilości, adresy i identyfikatory łańcucha są walidowane.
- Błędy kończą się kodem niezerowym. Teksty błędów nie są stabilnym API w wersji pre-alpha.
- Wynik dostawcy nie jest dowodem własności ani kryptograficznym dowodem salda.
