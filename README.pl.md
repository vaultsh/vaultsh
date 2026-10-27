<div align="center">

# Vaultsh

### Samodzielny portfel multi-chain — Beta 1.0

**Lokalnie · Jawna zgoda na sieć · Czarno-pomarańczowy terminal**

[![Licencja: GPL-3.0-only](https://img.shields.io/badge/License-GPL--3.0--only-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Beta%201.0-orange.svg)](#status-bety-i-ważne-ograniczenia)

</div>

**🌐 Dokumentacja / Documentation / Документация:** [English](README.md) · [Polski](README.pl.md) · [Русский](README.ru.md)

---

## Status bety i ważne ograniczenia

**Vaultsh 1.0.0-beta.1** dodaje wyprowadzanie portfeli dla poszczególnych sieci, kody QR publicznych adresów, odczyt sald/historii oraz opcjonalne wysyłanie aktywów natywnych dla Bitcoin, Ethereum Mainnet i Solana Mainnet, a także Monero przez oficjalny lokalny proces `monero-wallet-rpc`.

**To wersja beta, a nie audytowany portfel. Nie przechowuj w niej znacznych środków.** W środowisku budowania nie testowano jej na prawdziwych endpointach ani nie wysłano rzeczywistych transakcji. Testy lokalne używają atrap odpowiedzi RPC/Esplora. Przed rozważeniem użycia prawdziwych środków zainstaluj wszystkie zależności, uruchom pełne testy, zweryfikuj adresy względem oficjalnych wektorów, użyj testowych portfeli i zleć niezależny przegląd bezpieczeństwa.

## Obsługiwane funkcje

| Sieć | Portfel/ścieżka klucza | Odczyt | Wysyłanie | Ważne ograniczenie |
|---|---|---|---|---|
| Bitcoin Mainnet (BTC) | Angielskie BIP-39; BIP-84 `m/84'/0'/0'/0/0` | Saldo i pierwsza strona historii pojedynczego adresu | Lokalny podpis P2WPKH i wysłanie przez Esplora po dokładnym potwierdzeniu | Wybór UTXO obejmuje tylko potwierdzone UTXO pierwszego adresu odbiorczego. Brak skanowania adresów, sumowania całego portfela i wyszukiwania reszty. Reszta trafia na ścieżkę `/1/0`, której ta wersja nie skanuje. |
| Ethereum Mainnet (ETH) | BIP-39; BIP-44 `m/44'/60'/0'/0/0` | Saldo natywnego ETH | Lokalnie podpisana transakcja natywnego ETH, legacy EIP-155 | Wysyłka tylko natywnego ETH na chain ID 1. Brak ERC-20, kontraktów, EIP-1559, multisig, portfeli sprzętowych i śledzenia potwierdzeń. |
| Pozostałe profile EVM | Można odczytać ten sam format adresu | Saldo natywne Polygon PoS, Arbitrum One, Optimism i Base z kontrolą chain ID | Wysyłanie wyłączone | Te profile działają tylko do odczytu. `evm balance` nie oznacza wsparcia transakcji EVM. |
| Solana Mainnet Beta (SOL) | Angielskie BIP-39; `m/44'/501'/0'/0'` przez `bip-utils` i `solders` | Saldo natywnego SOL | Lokalnie podpisany transfer SOL, jawne wysłanie do RPC | Brak tokenów SPL, wykrywania adresów, historii i sprawdzania finalności. Potwierdzenie RPC nie gwarantuje potwierdzenia transakcji. |
| Monero Mainnet (XMR) | Oficjalne pliki portfela i obsługa kluczy przez lokalne `monero-wallet-rpc` | Adres główny i saldo portfela | `transfer` z `do_not_relay`, podgląd, a potem `relay_tx` po potwierdzeniu | Ziarno i pliki `.keys` Monero są zarządzane poza sejfem Vaultsh. Uruchomienie RPC/węzła i synchronizacja należą do użytkownika. |

Portfele BTC/ETH/SOL przechowują frazę BIP-39 wewnątrz uwierzytelnionego, zaszyfrowanego pliku Vaultsh. Monero używa własnego formatu i **nie jest przechowywane w tym sejfie**. Zwykła lista portfeli nie pokazuje fraz. Zapisz frazę offline po jej wyświetleniu podczas tworzenia portfela.

## Funkcje

- Pełnoekranowy interfejs Textual w czarno-pomarańczowym motywie, z kartami, tabelami, formularzami, nawigacją plików, nagłówkiem i stopką; awaryjny dashboard Rich.
- Dokumentacja po angielsku, polsku i rosyjsku oraz tłumaczenia głównych etykiet UI (`--lang en|pl|ru`).
- Lokalne szyfrowane sejfy, szyfrowanie uwierzytelnione, kopie zapasowe/odtwarzanie i rekordy portfeli BTC/ETH/SOL w schemacie v3.
- Tworzenie/odzyskiwanie portfeli BIP-39 BTC, ETH i SOL.
- Wyświetlanie QR i zapis PNG rozpoznawalnych publicznych adresów BTC/EVM/XMR/SOL. QR odrzuca spacje/frazy odzyskiwania i ciągi przypominające surowy klucz prywatny. Wykrycie formatu nie zastępuje sprawdzenia adresu na ekranie.
- Jawnie wybierane endpointy HTTPS Esplora/JSON-RPC; klienty blokują przekierowania i nie używają domyślnych proxy z otoczenia.
- Dwuetapowe zezwolenie sieciowe: `network_requests_enabled = true` **oraz** `--allow-network`.
- Dokładne przeliczanie kwot na jednostki bazowe bez arytmetyki zmiennoprzecinkowej.
- Podgląd transakcji (kwota, adres, opłata) i dokładne potwierdzenie tekstowe. Nie ma opcji `--yes` omijającej potwierdzenie.
- Integracja Monero jest ograniczona do lokalnego `monero-wallet-rpc`; zdalne endpointy wallet-RPC są odrzucane.

## Instalacja

Wymagany Python 3.12 lub nowszy. W katalogu głównym projektu:

```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# Linux / macOS / Termux: source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Jeżeli pip nie może połączyć się z PyPI, instalacja jest niepełna. Projekt wymaga zależności z `pyproject.toml`, m.in. `embit`, `eth-account`, `bip-utils`, `solders`, `qrcode[pil]`, `textual` i narzędzi testowych. Pominięty test nie oznacza, że funkcja została zweryfikowana.

## Pierwsze uruchomienie

```bash
vaultsh --lang pl              # albo --lang en / --lang ru
vaultsh --help
vaultsh version
vaultsh networks
vaultsh config-init ./vaultsh.toml
vaultsh config-check ./vaultsh.toml
```

Wygenerowana konfiguracja domyślnie wyłącza sieć. Edytuj `vaultsh.toml` dopiero, kiedy zamierzasz wysłać zapytanie:

```toml
[app]
app_name = "vaultsh"
telemetry_enabled = false
network_requests_enabled = true
tor_enabled = false
request_timeout_seconds = 15.0
```

`network_requests_enabled = true` zezwala na komendy sieciowe, lecz każda wymaga również `--allow-network`. `tor_enabled` musi pozostać `false`, ponieważ Vaultsh nie implementuje transportu Tor; po jego włączeniu komendy odmówią połączenia. Endpoint może zobaczyć sprawdzane adresy i metadane połączenia.

## Utworzenie sejfu i portfeli

```bash
vaultsh vault init ./main.vault --label "Main Vault"
vaultsh wallet create --vault ./main.vault --label "BTC savings" --network bitcoin
vaultsh wallet create --vault ./main.vault --label "ETH account" --network ethereum
vaultsh wallet create --vault ./main.vault --label "SOL account" --network solana
vaultsh wallet list --vault ./main.vault
```

Aby zaimportować angielską frazę BIP-39 (12 lub 24 słowa), użyj `vaultsh wallet recover --vault ./main.vault --network ethereum` (albo `bitcoin` / `solana`). Ta beta obsługuje wyłącznie pustą opcjonalną frazę BIP-39. Polecenia wysyłania wymagają właściwego ID portfela i pliku sejfu.

**Chroń frazę i hasło sejfu osobno.** Każdy, kto pozna frazę, może kontrolować portfel. Nie wklejaj jej do zgłoszeń, czatu, historii powłoki, notatek w chmurze ani zrzutów ekranu. Zaszyfrowany sejf nie chroni frazy po jej wyświetleniu lub skopiowaniu poza sejf.

## Kody QR adresów odbiorczych

Wyświetl kod QR portfela zapisanego w sejfie:

```bash
vaultsh wallet qr WALLET_ID --vault ./main.vault
vaultsh wallet qr WALLET_ID --vault ./main.vault --output ./receive-address.png
```

Lub utwórz QR z publicznego adresu:

```bash
vaultsh qr bc1qPUBLICZNYADRES
vaultsh qr 0xPUBLICZNY_ADRES_40_ZNAKÓW --output ./eth-address.png
```

QR zawiera wyłącznie adres publiczny. Nie jest żądaniem płatności z kwotą, a sprawdzanie formatu nie jest pełną weryfikacją sumy kontrolnej każdego typu adresu. Przed udostępnieniem sprawdź adres odczytany z kodu.

## Zapytania sieciowe i wysyłanie

Wszystkie przykłady wymagają `network_requests_enabled = true`, jawnego endpointu i flagi `--allow-network`. Korzystaj z zaufanych endpointów; nie pokazuj w zrzutach ekranu adresów URL zawierających token dostępu.

### Bitcoin Mainnet

```bash
vaultsh bitcoin balance ADDRESS --endpoint https://TWOJ-ESPLORA/api --config ./vaultsh.toml --allow-network
vaultsh bitcoin history ADDRESS --endpoint https://TWOJ-ESPLORA/api --config ./vaultsh.toml --allow-network --limit 10
vaultsh bitcoin send --wallet-id WALLET_ID --vault ./main.vault --to bc1qODBIORCA --amount 0.0001 --endpoint https://TWOJ-ESPLORA/api --config ./vaultsh.toml --allow-network --max-fee-sats 100000
```

Wysyłka BTC obejmuje tylko potwierdzone UTXO pierwszego adresu odbiorczego. Nie skanuje indeksów adresów ani UTXO z gałęzi reszty. Nie traktuj salda i historii jednego adresu jako pełnego stanu portfela.

### Ethereum Mainnet

```bash
vaultsh ethereum balance 0xADRES_40_ZNAKOW --endpoint https://TWOJ-ETH-RPC --config ./vaultsh.toml --allow-network
vaultsh ethereum send --wallet-id WALLET_ID --vault ./main.vault --to 0xODBIORCA --amount 0.001 --endpoint https://TWOJ-ETH-RPC --config ./vaultsh.toml --allow-network --max-fee-eth 0.1
```

Wysyłanie dotyczy wyłącznie natywnego ETH na chain ID `1`. Odczyt salda EVM działa też dla Polygon PoS (`137`), Arbitrum One (`42161`), Optimism (`10`) i Base (`8453`), ale wysyłanie w tych sieciach jest wyłączone. Obecny transfer używa transakcji legacy z `gasPrice`, a nie EIP-1559.

### Solana Mainnet Beta

```bash
vaultsh solana balance PUBLICZNY_ADRES_SOL --endpoint https://TWOJ-SOLANA-RPC --config ./vaultsh.toml --allow-network
vaultsh solana send --wallet-id WALLET_ID --vault ./main.vault --to ODBIORCA_SOL --amount 0.01 --endpoint https://TWOJ-SOLANA-RPC --config ./vaultsh.toml --allow-network --max-fee-sol 0.01
```

Klient sprawdza hash genesis endpointu Solana Mainnet, tworzy i podpisuje lokalnie transfer natywnego SOL, a wysyła go dopiero po potwierdzeniu. Odpowiedź `sendTransaction` potwierdza przyjęcie zgłoszenia, nie finalność transakcji.

### Monero Mainnet

Vaultsh nie implementuje własnej obsługi kluczy/ziarna Monero. Zainstaluj Monero z oficjalnego projektu i uruchom lokalnie `monero-wallet-rpc` obok zsynchronizowanego `monerod` lub świadomie wybranego węzła. Przykład (dostosuj ścieżki i dane uwierzytelniające):

```bash
monero-wallet-rpc --rpc-bind-ip 127.0.0.1 --rpc-bind-port 18082 \\
  --wallet-dir ./monero-wallets \\
  --rpc-login vaultshrpc:ZASTAP_DŁUGIM_HASŁEM_RPC \\
  --daemon-address http://127.0.0.1:18081
```

Zakłada to dostępność `monerod` pod `127.0.0.1:18081`. Nie wystawiaj wallet-RPC na publicznym interfejsie.

```bash
vaultsh monero create-wallet savings --rpc-username vaultshrpc --config ./vaultsh.toml --allow-network
vaultsh monero address --rpc-username vaultshrpc --config ./vaultsh.toml --allow-network
vaultsh monero balance --rpc-username vaultshrpc --config ./vaultsh.toml --allow-network
vaultsh monero send --to ODBIORCA_XMR_MAINNET --amount 0.01 --rpc-username vaultshrpc --config ./vaultsh.toml --allow-network
```

Vaultsh ukrywa wpisywanie hasła RPC oraz hasła portfela. `monero-wallet-rpc` przechowuje portfel i pliki kluczy w swoim katalogu, poza sejfem Vaultsh. Zabezpiecz kopię portfela Monero i ziarno. To konfiguracja demona decyduje, z którym węzłem działa portfel; Vaultsh weryfikuje zwrócony adres Mainnet, ale nie zarządza demonem ani go nie audytuje.

## Bezpieczeństwo transakcji

- Program przygotowuje i lokalnie podpisuje transakcje BTC/ETH/SOL albo prosi `monero-wallet-rpc` o utworzenie transakcji XMR bez wysyłania.
- Wyświetla adres, kwotę, opłatę i szczegóły sieciowe, a następnie wymaga wpisania dokładnej frazy potwierdzającej. Nie ma `--yes` omijającego tę ochronę.
- Podpisana transakcja może zostać wysłana przez każdego, kto ją zdobędzie przed retransmisją. Nie umieszczaj jej w logach ani na czacie. Ukrycie jej w `repr` nie oznacza wyzerowania pamięci Pythona.
- Odpowiedzi endpointu mogą być fałszywe lub nieaktualne. Hash/signatura zwykle oznacza przyjęcie zgłoszenia, nie potwierdzenie transakcji.
- Testuj na jednorazowym portfelu i bardzo małych kwotach. Testy jednostkowe nie dowodzą bezpieczeństwa rzeczywistych operacji.

## Testowanie i rozwój

```bash
python -m compileall -q src tests
python -m pytest --cov=vaultsh --cov-report=term-missing -q
ruff check .
mypy src/vaultsh
```

Część testów wymaga wszystkich zależności runtime oraz osobnych testów na kontrolowanych węzłach. Testy jednostkowe używają atrap i nie wysyłają transakcji. Zobacz [wyniki testów](docs/TEST_RESULTS.md), [model bezpieczeństwa](docs/SECURITY_MODEL.md) i [adaptery sieciowe](docs/NETWORK_ADAPTERS.md).

## Brakujące funkcje

- Brak niezależnego audytu bezpieczeństwa i zweryfikowanego procesu wydawniczego.
- Brak skanowania adresów i limitu gap dla całego portfela; saldo/wysyłka BTC dotyczy pierwszego adresu, a gałąź reszty nie jest skanowana.
- Brak tokenów ERC-20, wywołań kontraktów, podpisywania EVM poza Ethereum Mainnet, EIP-1559 oraz monitorowania receipt/finality.
- Brak tokenów SPL, historii transakcji i sprawdzania potwierdzeń Solany.
- Pliki Monero nie są importowane ani szyfrowane przez sejf Vaultsh; do odzyskiwania i kopii używa się oficjalnych narzędzi Monero.
- Brak transportu Tor, portfeli sprzętowych, multisig, interfejsu cold-signing i pełnych testów z prawdziwymi węzłami.
- Interfejs Textual udostępnia obecnie podstawowe operacje sejfu/portfeli i formularze odczytu; wysyłanie transakcji odbywa się przez komendy CLI opisane wyżej.

## Licencja

Vaultsh jest dystrybuowany na licencji `GPL-3.0-only`. Zobacz [LICENSE](LICENSE).
