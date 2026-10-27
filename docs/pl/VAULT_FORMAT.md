# Format zaszyfrowanego sejfu

**🌐 Język:** [English](../VAULT_FORMAT.md) · [Polski](VAULT_FORMAT.md) · [Русский](../ru/VAULT_FORMAT.md) · [README](../../README.pl.md)

## Warstwy pliku

Plik składa się z nagłówka szyfrowania oraz zaszyfrowanego dokumentu JSON. Zawartość dokumentu nie jest czytelna bez wyprowadzenia klucza z hasła i poprawnego uwierzytelnienia.

## Koperta szyfrowania

- Znacznik: `VSHV`; wersja koperty: `1`.
- Wyprowadzanie klucza z hasła: Scrypt; parametry domyślne `N = 2**15`, `r = 8`, `p = 1`.
- Sól: 16 losowych bajtów z systemu operacyjnego.
- Nonce AES-GCM: 12 bajtów; klucz AES-256: 32 bajty; tag uwierzytelniający zapewnia wykrywanie modyfikacji.
- Nagłówek jest uwierzytelniany jako dodatkowe dane.
- Przed kosztowną derivacją walidowane są granice parametrów: `N` pomiędzy `2**14` i `2**16` i będące potęgą dwójki, `r` od 1 do 8 oraz `p` od 1 do 4.
- Warstwa pliku ogranicza wejście do 64 MiB.

## Dokument wewnętrzny

Wspólne pola: `schema = vaultsh.vault`, obsługiwana liczba `schema_version`, mały UUID `vault_id`, niepusta etykieta do 80 znaków bez znaków sterujących, `created_at` w ISO 8601 ze strefą czasową oraz lista `wallets`.

### Schemat v1

Zawiera metadane sejfu i pustą listę portfeli; sam w sobie nie oznacza, że zapisano sekret portfela.

### Schemat v2

Rekord Bitcoin obejmuje `wallet_id`, `label`, `network = bitcoin-mainnet`, adres pierwszego odbiorczego Native SegWit P2WPKH, ścieżkę `m/84'/0'/0'/0/0`, znacznik czasu oraz angielską frazę BIP-39 składającą się z 12 lub 24 słów.

## EVM i migracja

Ten schemat nie przechowuje kluczy EVM; adapter EVM jest tylko do odczytu. Starsze dokumenty v1 pozostają czytelne. Samo sprawdzenie sejfu nie migruje formatu; dodanie portfela Bitcoin zapisuje nowy dokument v2 z atomową zamianą zaszyfrowanego pliku.

## Obsługa sekretów i kopii

Zwykła lista portfeli nie pokazuje frazy. Jej ujawnienie wymaga potwierdzenia użytkownika i odblokowania sejfu; mimo to terminal może być nagrywany. Kopia jest kopią zaszyfrowanego pliku, więc chroni zawartość szyfrowaniem, ale osoba z plikiem może próbować zgadywać hasło offline. Chroń hasło i frazę oddzielnie.

## Zgodność

Format jest przedprodukcyjny i nie ma niezależnego audytu. Zachowanie formatu może zmienić się przed stabilnym wydaniem; przed aktualizacją wykonuj zaszyfrowaną kopię i sprawdzaj możliwość odtworzenia.
