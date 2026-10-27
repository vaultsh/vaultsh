# Model bezpieczeństwa

**🌐 Język:** [English](../SECURITY_MODEL.md) · [Polski](SECURITY_MODEL.md) · [Русский](../ru/SECURITY_MODEL.md) · [README](../../README.pl.md)

## Chronione zasoby

- Frazy odzyskiwania przechowywane wewnątrz szyfrowanego sejfu.
- Hasło sejfu oraz pliki sejfu i kopii zapasowych.
- Adresy publiczne i metadane endpointów związane z zapytaniami sieciowymi.
- Integralność informacji wyświetlanych użytkownikowi oraz danych salda otrzymanych od dostawcy.

## Założenia

Program może działać na urządzeniu kontrolowanym przez użytkownika, ale nie może ochronić sekretów przed złośliwym systemem, keyloggerem, przechwytywaniem terminala, złośliwym pakietem, przejętym endpointem lub osobą, która pozna frazę odzyskiwania. Publiczne blockchainy są publiczne; prywatność transportu nie usuwa śladów on-chain.

## Zaimplementowane mechanizmy

- Scrypt do wyprowadzania klucza z hasła i AES-256-GCM z uwierzytelnianiem danych.
- Losowe sole i nonce pochodzące z systemu operacyjnego; nagłówek jest uwierzytelniany jako dodatkowe dane.
- Walidacja dokumentu po odszyfrowaniu oraz atomowe zapisy.
- Lista portfeli pokazuje podsumowania publiczne, nie frazy.
- Ujawnienie frazy wymaga potwierdzenia i odblokowania sejfu.
- Zapytania sieciowe wymagają zgody w konfiguracji i flagi `--allow-network`.
- Jawny endpoint; HTTPS dla zdalnych adresów; odrzucane są dane logowania, query/fragment i segmenty traversal.
- Limity rozmiaru odpowiedzi i timeouty, blokowane przekierowania i ignorowane automatyczne proxy.
- EVM weryfikuje JSON-RPC ID i chain ID; adresy mieszane wymagają EIP-55.
- Historia Bitcoin waliduje TXID/status i ogranicza liczbę rekordów.

## Znane luki

- Nie wykonano niezależnego audytu kryptograficznego ani aplikacyjnego.
- Python nie gwarantuje wyzerowania sekretów z pamięci.
- Fraza jest widoczna w terminalu podczas tworzenia; zrzut ekranu lub nagranie może ją przechwycić.
- Kto zna frazę odzyskiwania, może odzyskać portfel niezależnie od hasła sejfu.
- Sejf przechowuje obecnie rekordy Bitcoin; EVM jest tylko do odczytu i nie ma kluczy prywatnych.
- Saldo/historia BTC dotyczą jednego adresu, a salda EVM są danymi wybranego dostawcy; stan nie jest niezależnie dowodzony.
- Walidacja endpointu nie czyni dostawcy zaufanym ani nie eliminuje obserwacji sieciowej.
- Tor, tokeny, historia EVM, budowanie/podpisywanie/wysyłanie transakcji i Monero nie są zaimplementowane.
- Testy atrap nie potwierdzają interoperacyjności z realnymi usługami ani bezpieczeństwa.

## Przed użyciem prawdziwych środków

Niezależny audyt, testy na wszystkich platformach, sprawdzenie wektorów, niezależny test kopii zapasowej i odzyskiwania, przegląd zależności i pełny proces tworzenia/podpisywania transakcji. Do tego czasu traktuj program jako eksperymentalny.
