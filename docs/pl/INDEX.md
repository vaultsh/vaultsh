# Indeks dokumentacji — Vaultsh 1.0.0-beta.1

**Języki:** [English](../INDEX.md) · [Polski](INDEX.md) · [Русский](../ru/INDEX.md) · [README PL](../../README.pl.md)

Vaultsh to lokalny portfel self-custody w wersji beta. Nie przeszedł niezależnego audytu. Nie przechowuj w nim znacznych środków. Szczególnie nie używaj wysyłania BTC z prawdziwymi środkami, dopóki nie zostanie ukończone wykrywanie adresów i środków reszty.

## Funkcje zaimplementowane
- Zaszyfrowany lokalny sejf i rekordy portfeli BTC/ETH/SOL.
- Tworzenie i odzyskiwanie portfeli z angielskiej frazy BIP-39 (12/24 słowa, pusta dodatkowa fraza).
- QR/PNG dla rozpoznawanych formatów publicznych adresów BTC/EVM/XMR/SOL; nie jest to uniwersalna weryfikacja sumy kontrolnej.
- Odczyt salda/historii jednego adresu BTC i sald natywnych pięciu sieci EVM.
- Podpisywanie lokalne i wysyłanie natywnego BTC/ETH/SOL po podglądzie i dokładnym potwierdzeniu tekstowym.
- Obsługa Monero przez oficjalne lokalne `monero-wallet-rpc`; pliki portfela i seed Monero pozostają poza sejfem Vaultsh.
- Interfejs Textual i awaryjny dashboard Rich.

## Najważniejsze ograniczenia
- BTC: wyszukiwanie obejmuje tylko potwierdzone UTXO pierwszego adresu odbiorczego. Reszta trafia na `/1/0`, którego Vaultsh jeszcze nie skanuje. Nie wysyłaj prawdziwego BTC.
- ETH: tylko natywne ETH Mainnet (chain ID 1), transakcje legacy `gasPrice`; bez ERC-20/EIP-1559 i śledzenia finalności.
- SOL: tylko natywne SOL, bez SPL i finality polling.
- Pozostałe profile EVM są tylko do odczytu.
- Monero wymaga prawidłowo skonfigurowanego `monero-wallet-rpc` na loopback.
- Brak działającego transportu Tor, portfeli sprzętowych, multisig i niezależnego audytu.

## Dokumenty
- [Architektura](../ARCHITECTURE.md), [CLI](../CLI_REFERENCE.md), [Konfiguracja](../CONFIGURATION.md), [Sieci](../NETWORK_ADAPTERS.md), [Format sejfu](../VAULT_FORMAT.md), [Model bezpieczeństwa](../SECURITY_MODEL.md), [Wyniki testów](../TEST_RESULTS.md), [Rozwój](../DEVELOPMENT.md), [Interfejs](../INTERFACE.md), [Roadmapa](../ROADMAP.md).

Ostatni lokalny wynik: **194 zaliczone, 7 pominiętych, 53% pokrycia**. Nie wysłano transakcji na prawdziwej sieci. Szczegóły w [raporcie testów](../TEST_RESULTS.md).
