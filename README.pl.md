<div align="center">

# Vaultsh

### Prywatnościowy fundament wielołańcuchowego portfela kryptowalutowego w terminalu

**Lokalnie. Prywatność domyślnie. Jawna zgoda na sieć.**

[![License: GPL-3.0-only](https://img.shields.io/badge/License-GPL--3.0--only-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Pre--alpha-orange.svg)](#status-projektu)

</div>

**🌐 Dokumentacja:** [English](README.md) · [Polski](README.pl.md) · [Русский](README.ru.md)

---

## Status projektu

**Vaultsh 0.6.0 to wersja pre-alpha, bez niezależnego audytu. Nie używaj jej do przechowywania ani przesyłania prawdziwych środków.** Projekt łączy lokalne szyfrowane sejfy i kopie zapasowe z tworzeniem/odzyskiwaniem portfela Bitcoin Mainnet offline oraz jawnie autoryzowanym odczytem danych sieciowych.

Dostępne funkcje Bitcoin obejmują ograniczoną ścieżkę BIP-39/BIP-84, saldo jednego adresu i pierwszą stronę historii transakcji adresu przez wskazany endpoint Esplora. W pięciu sieciach EVM — Ethereum, Polygon PoS, Arbitrum One, Optimism i Base — dostępny jest wyłącznie odczyt natywnego salda przez wskazany endpoint JSON-RPC. Nie są dostępne klucze EVM, tokeny ERC-20, tworzenie transakcji, podpisywanie ani wysyłanie. Monero nie jest zaimplementowane.

Projekt napisano w Pythonie. Celem są Windows 10/11, Linux i Android przez Termux, ale każda platforma wymaga osobnych testów zgodności.

## Co nowego w 0.6.0

- Odczyt pierwszej strony historii transakcji pojedynczego adresu Bitcoin przez wybrany endpoint Esplora (maksymalnie 25 wpisów).
- Odczyt natywnego salda dla Ethereum (chain ID 1), Polygon PoS (137), Arbitrum One (42161), Optimism (10) i Base (8453). Przed odczytem saldo klient sprawdza `eth_chainId`.
- Sprawdzanie formatu adresu EVM i sumy kontrolnej EIP-55 dla adresów mieszanych małych i wielkich liter.
- Ruch sieciowy jest wyłączony domyślnie. Wymagane są jednocześnie `network_requests_enabled = true` w TOML oraz `--allow-network`.
- Endpoint trzeba wskazać jawnie. Zdalne endpointy wymagają HTTPS; HTTP jest dozwolone wyłącznie dla localhost/loopback. Przekierowania i automatyczne proxy ze zmiennych środowiskowych są wyłączone.

## Macierz funkcji

| Funkcja | Bitcoin Mainnet | Sieci EVM (5 profili) | Monero |
|---|---|---|---|
| Tworzenie/odzyskiwanie offline | Ograniczone BIP-39/BIP-84 | Niezaimplementowane | Niezaimplementowane |
| Walidacja adresu | Obsługiwane formaty Mainnet przez `embit` | Format `0x` i EIP-55 dla liter mieszanych | Niezaimplementowane |
| Odczyt salda | Tak, pojedynczy adres przez Esplora | Tak, natywne aktywo przez JSON-RPC | Niezaimplementowane |
| Historia transakcji adresu | Pierwsza strona, maks. 25 rekordów | Niezaimplementowane | Niezaimplementowane |
| Odkrywanie całego portfela | Niezaimplementowane | Niezaimplementowane | Niezaimplementowane |
| Podgląd/podpisywanie/wysyłanie transakcji | Niezaimplementowane | Niezaimplementowane | Niezaimplementowane |
| Tokeny | Nie dotyczy adaptera | ERC-20 niezaimplementowane | Niezaimplementowane |
| Transport Tor | Niezaimplementowany | Niezaimplementowany | Niezaimplementowany |

Wyniki salda i historii pochodzą od wybranego dostawcy i nie są kryptograficznym dowodem własności ani kompletnego stanu portfela.

## Wyniki testów

Najnowsze lokalne uruchomienie z 27.10.2026 zakończyło się wynikiem **144 testy zaliczone, 4 pominięte, pokrycie linii 82%**. Polecenie: `pytest --cov=vaultsh --cov-report=term-missing -q`, Python 3.13.5. Cztery testy pominięto, ponieważ w środowisku nie było zależności `embit` i `eth-utils`. Testy sieciowe korzystają z atrap; nie wykonywano zapytań do publicznych API. To nie jest certyfikat bezpieczeństwa. Szczegóły: [raport testów](docs/pl/TEST_RESULTS.md).

## Dokumentacja

- [Indeks dokumentacji](docs/pl/INDEX.md)
- [Architektura](docs/pl/ARCHITECTURE.md)
- [Referencja CLI](docs/pl/CLI_REFERENCE.md)
- [Konfiguracja](docs/pl/CONFIGURATION.md)
- [Format sejfu](docs/pl/VAULT_FORMAT.md)
- [Model bezpieczeństwa](docs/pl/SECURITY_MODEL.md)
- [Adaptery sieciowe](docs/pl/NETWORK_ADAPTERS.md)
- [Wyniki testów](docs/pl/TEST_RESULTS.md)
- [Rozwój i testowanie](docs/pl/DEVELOPMENT.md)
- [Roadmapa](docs/pl/ROADMAP.md)
- [Współtworzenie](docs/pl/CONTRIBUTING.md)
- [Polityka bezpieczeństwa](docs/pl/SECURITY.md)
- [Historia zmian](docs/pl/CHANGELOG.md)

## Język interfejsu

Panel startowy i główne ekrany informacyjne obsługują angielski, polski i rosyjski. Ustaw język przed poleceniem: `vaultsh --lang pl` lub `vaultsh --lang ru about`. Szczegółowa pomoc dla poleceń, część pytań i komunikatów błędów pozostaje w tej wersji po angielsku.

## Instalacja

Wymagany Python 3.12 lub nowszy. W katalogu głównym repozytorium: 

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS/Termux: source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

`embit` udostępnia prymitywy BIP-39/BIP-32/BIP-84, a `eth-utils` i `eth-hash[pycryptodome]` służą do walidacji sumy EIP-55. Zależności należy instalować w zaufanym środowisku i przeglądać przed użyciem produkcyjnym.

## Szybki start

Utwórz zaszyfrowany sejf. Hasło jest wpisywane bez wyświetlania i musi mieć co najmniej 12 znaków:

```bash
vaultsh vault init ./main.vault --label "Główny sejf"
vaultsh wallet create --vault ./main.vault --label "Bitcoin Main"
vaultsh wallet list --vault ./main.vault
```

Przy tworzeniu portfela fraza odzyskiwania zostanie pokazana do zapisania offline i będzie przechowywana w zaszyfrowanym ładunku sejfu. Każdy, kto pozna frazę, może kontrolować portfel. Przed realnym użyciem wymagany jest audyt i dużo szersze testy.

## Zapytania sieciowe i prywatność

Przykład odczytu salda EVM (zastąp adres i endpoint własnymi wartościami):

```bash
vaultsh evm balance 0xYOUR_ADDRESS --chain polygon --endpoint https://YOUR-RPC --config ./vaultsh.toml --allow-network
```

Wybrany endpoint poznaje sprawdzany adres i metadane połączenia. Tor nie jest zaimplementowany. Jeśli `tor_enabled = true`, polecenia sieciowe odmawiają bezpośredniego połączenia. Nie istnieje domyślny publiczny dostawca.

## Rozwój

```bash
pytest --cov=vaultsh --cov-report=term-missing -q
ruff check .
mypy src/vaultsh
git diff --check
```

Ruff i mypy trzeba zainstalować z zależnościami `dev`. Raportuj wyłącznie kontrole, które faktycznie uruchomiono.

## Licencja i zastrzeżenia

Projekt jest objęty licencją GPL-3.0-only. Nie jest niezależnie audytowany. Nie gwarantuje anonimowości. Nie podpisuje ani nie wysyła transakcji. Nie używaj do prawdziwych środków.
