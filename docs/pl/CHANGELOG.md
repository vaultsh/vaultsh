# Historia zmian — polski skrót wydań

**🌐 Język:** [English](../../CHANGELOG.md) · [Polski](CHANGELOG.md) · [Русский](../ru/CHANGELOG.md)

## 🚧 [Unreleased]

### ✨ Dodano
- Dodano polskie i rosyjskie README oraz pełne zbiory dokumentacji językowej z odnośnikami do przełączania języka.
- Dodano `--lang en|pl|ru` dla panelu startowego i głównych ekranów informacyjnych.
- Dodano pogrupowany panel poleceń, pierwszy start krok po kroku, ostrzeżenie pre-alpha i przypomnienie o podwójnej zgodzie na sieć.
- Dodano testy regresyjne panelu, przeglądu sieci, ekranów informacyjnych PL/RU i obsługi nieznanego kodu języka.

### 🔄 Zmieniono
- Uporządkowano tabele i panele terminala; rozdzielono długie polecenia na osobne wiersze.
- Zaktualizowano lokalne wyniki testów do 144 zaliczonych, 4 pominiętych i 82% pokrycia linii.

### 🛡️ Uwagi
- Lokalizacja działania CLI obejmuje obecnie panel startowy i główne ekrany informacyjne. Szczegółowa pomoc, część promptów i komunikatów błędów pozostają po angielsku.
- Numer wersji aplikacji pozostaje 0.6.0 do czasu formalnego wydania.

## 🚀 [0.6.0] — 2026-10-27

### ✨ Dodano
- Odczyt pierwszej strony historii transakcji pojedynczego adresu Bitcoin przez Esplora, maksymalnie 25 rekordów.
- Odczyt natywnego salda Ethereum, Polygon PoS, Arbitrum One, Optimism i Base przez JSON-RPC z kontrolą `chainId`.
- Walidację adresów EVM i checksumy EIP-55 dla adresów o mieszanym zapisie.
- Ograniczenia odpowiedzi HTTP, timeouty, blokowanie przekierowań oraz testy atrap sieciowych.

### 🛡️ Ograniczenia
- Brak portfeli/kluczy EVM, tokenów ERC-20, Monero, podpisywania i wysyłania transakcji oraz transportu Tor.
- Wyniki salda i historii są danymi dostawcy, a nie dowodem kryptograficznym.

## 🚀 [0.4.5] — 2026-10-27

- Dodano jawnie autoryzowany odczyt salda pojedynczego adresu Bitcoin.
- Dodano politykę HTTPS dla zdalnych endpointów, limity odpowiedzi i walidację salda.

## 🚀 [0.3.0] — 2026-10-27

- Dodano ograniczone tworzenie i odzyskiwanie portfela Bitcoin Mainnet BIP-39/BIP-84 oraz rekordy portfeli w schemacie sejfu v2.
- Dodano listowanie metadanych publicznych bez fraz odzyskiwania.

## 🚀 [0.2.0] — 2026-10-27

- Dodano komendy inicjalizacji, sprawdzania, kopii i odtwarzania zaszyfrowanego sejfu oraz generowanie i walidację konfiguracji TOML.

## 🚀 [0.1.0] — 2026-10-27

- Dodano początkowy układ pakietu Python, CLI Typer/Rich, konfigurację, prymitywy szyfrowania, kopie zapasowe i bazowe testy.
