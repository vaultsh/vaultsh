# Roadmapa

**🌐 Język:** [English](../ROADMAP.md) · [Polski](ROADMAP.md) · [Русский](../ru/ROADMAP.md) · [README](../../README.pl.md)

## Stan bazowy: 0.6.0

- [x] Interfejs Typer/Rich, polecenia i konfiguracja TOML bez sekretów.
- [x] Scrypt i AES-256-GCM dla lokalnego zaszyfrowanego sejfu.
- [x] Odczyt schematu sejfu v1 i rekordy portfeli Bitcoin v2.
- [x] Zaszyfrowane kopie zapasowe oraz odtwarzanie.
- [x] Ograniczone tworzenie i odzyskiwanie Bitcoin Mainnet BIP-39/BIP-84 offline.
- [x] Odczyt salda jednego adresu BTC i pierwszej strony historii.
- [x] Odczyt natywnego salda pięciu profili EVM z weryfikacją chain ID.
- [x] Jawne endpointy, podwójna zgoda sieciowa, timeouty, limity odpowiedzi i blokowanie przekierowań.
- [x] Testy lokalne atrapowanych odpowiedzi i dokumentacja angielska.
- [x] README i dokumentacja po polsku oraz rosyjsku; częściowo zlokalizowany dashboard CLI.
- [ ] Potwierdzone wyniki CI na hostowanych Windows/Linux.
- [ ] Uruchomienie wszystkich wektorów z pełnym zestawem zależności.
- [ ] Niezależny audyt bezpieczeństwa i przegląd zależności.

## Etap 1 — fundament projektu

- [x] Układ pakietu i CLI Typer/Rich.
- [x] Testy bazowe i konfiguracja narzędzi.
- [x] Szablon TOML i polecenia walidujące.
- [x] Model zagrożeń, instrukcja współtworzenia i dokumentacja.
- [ ] Regularne, potwierdzone uruchomienia CI na Windows/Linux.
- [ ] Audyt zależności/licencji i pochodzenia wydań.

## Etap 2 — bezpieczny zapis lokalny

- [x] Wersjonowany dokument wewnątrz szyfrowanego kontenera.
- [x] Walidacja parametrów Scrypt, AES-256-GCM, zapisy atomowe i kopie.
- [x] Ograniczone rekordy Bitcoin z materiałem odzyskiwania w zaszyfrowanym payloadzie.
- [ ] Niezależny przegląd formatu, obsługi sekretów i przywracania kopii.
- [ ] Strategia migracji/eksportu przed dodaniem wielu rodzin portfeli.

## Etap 3 — integracja blockchain

- [x] Pierwszy przepływ offline Bitcoin BIP-39/BIP-84.
- [x] Odczyt salda i historii pojedynczego adresu BTC.
- [x] Natywne saldo pięciu profili EVM.
- [ ] Odkrywanie adresów Bitcoin, gap limit, adresy reszty i pełne saldo/historia portfela.
- [ ] Tworzenie/odzyskiwanie EVM i bezpieczne rekordy kluczy prywatnych.
- [ ] Tokeny ERC-20 i historia EVM.
- [ ] Przegląd transakcji, opłaty/gas, budowanie oraz podpisywanie offline.
- [ ] Niezależna kontrola przed użyciem prawdziwych środków.

## Etap 4 — prywatność i kolejne sieci

- [x] Wybór endpointów Esplora i JSON-RPC przez użytkownika.
- [ ] Prawdziwy, przetestowany transport Tor.
- [ ] Monero z własnym modelem kluczy i oficjalnymi wektorami testowymi.
- [ ] Dodatkowe sieci EVM dopiero po weryfikacji chain ID i semantyki aktywów.
- [ ] Testy sieci z kontrolowanymi węzłami i odpowiedziami złośliwymi.

## Etap 5 — stabilizacja wydania

- [ ] Testy kompatybilności Windows, Linux i Android/Termux.
- [ ] CI i blokujące wydanie kontrole jakości.
- [ ] Audyty zależności, licencji i łańcucha dostaw.
- [ ] Niezależny audyt bezpieczeństwa.
- [ ] Kryteria stabilnego wydania i procedura odpowiedzialnego zgłaszania błędów.

## Warunki przed użyciem prawdziwych środków

Niezależny audyt, kompletny zestaw wektorów, odtwarzanie kopii testowane na oddzielnym systemie, sprawdzona obsługa sekretów i podpisywania, CI na obsługiwanych platformach oraz jawna procedura reagowania na incydenty.
