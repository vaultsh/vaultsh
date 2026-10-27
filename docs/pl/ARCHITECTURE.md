# Architektura

**🌐 Język:** [English](../ARCHITECTURE.md) · [Polski](ARCHITECTURE.md) · [Русский](../ru/ARCHITECTURE.md) · [README](../../README.pl.md)

## Układ źródeł

Kod aplikacji znajduje się w `src/vaultsh/`, a testy w `tests/`. Główne moduły: `cli.py`, `config.py`, `core/`, `crypto/`, `storage/`, `networks/`, `privacy/` i `ui/`.

## Granice odpowiedzialności

- **CLI (`cli.py`)** — parsowanie poleceń, pytania do użytkownika, formatowanie wyników i kody wyjścia. Nie powinien implementować kryptografii ani protokołów sieciowych.
- **Konfiguracja (`config.py`)** — waliduje niesekretne preferencje z TOML. Nie przechowuje haseł, fraz ani kluczy.
- **Kryptografia i magazyn (`crypto/`, `storage/`)** — szyfrowanie uwierzytelnione, format dokumentu sejfu, atomowe zapisy oraz kopie zapasowe.
- **Model domeny (`core/`)** — wspólne typy i reguły walidacji niezależne od interfejsu.
- **Adaptery (`networks/`)** — standardy specyficzne dla sieci i komunikacja. Bitcoin i EVM nie mogą współdzielić założeń dotyczących derivacji, adresów, jednostek lub transakcji.
- **Prywatność (`privacy/`)** — polityka dostępu do sieci oraz ustawienia Tor. Flaga Tor nie oznacza działającego transportu.
- **UI (`ui/`)** — panele Rich, ekrany startowe i tłumaczenia głównego interfejsu.

## Adaptery dostępne obecnie

`networks/bitcoin/wallet.py` używa `embit` do angielskich fraz BIP-39 i pierwszego adresu BIP-84 Mainnet. `networks/bitcoin/client.py` odczytuje saldo i pierwszą stronę historii pojedynczego adresu Esplora. `networks/ethereum/client.py` ma listę pięciu profili EVM, waliduje adresy i checksumę EIP-55 oraz sprawdza `eth_chainId` przed `eth_getBalance`. Nie tworzy kluczy EVM.

## Kierunek zależności

UI może wywoływać funkcje domenowe i adaptery, lecz logika domenowa nie powinna zależeć od CLI. Adaptery nie powinny modyfikować konfiguracji ani zapisywać sekretów samodzielnie. Testy jednostkowe sieci używają fałszywych odpowiedzi — nie łączą się z publicznymi usługami.

## Zasady rozbudowy

- Dodaj sieć dopiero po wskazaniu standardów, jednostek, formatu adresów i oficjalnych wektorów testowych.
- Waliduj i przeliczaj wartości finansowe na liczbach całkowitych w najmniejszych jednostkach.
- Dodaj testy błędnych i złośliwych odpowiedzi, limitów, przekierowań oraz odmowy dostępu do sieci bez zgody.
- Nie deklaruj implementacji tylko dlatego, że istnieje folder lub protokół bazowy.
