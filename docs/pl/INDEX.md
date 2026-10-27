# Dokumentacja Vaultsh — język polski

**🌐 Język:** [English](../INDEX.md) · [Polski](INDEX.md) · [Русский](../ru/INDEX.md) · [README po polsku](../../README.pl.md)

Dokumentacja dotyczy kodu w wersji bazowej **0.6.0** oraz niezapisanych jeszcze jako wydanie poprawek interfejsu i tłumaczeń. Vaultsh jest projektem pre-alpha, nieaudytowanym portfelem.

## Dokumentacja użytkownika

- [README](../../README.pl.md) — opis, instalacja, szybki start, funkcje i ostrzeżenia.
- [Referencja CLI](CLI_REFERENCE.md) — polecenia i opcje.
- [Konfiguracja](CONFIGURATION.md) — ustawienia TOML i podwójna zgoda na sieć.
- [Adaptery sieciowe](NETWORK_ADAPTERS.md) — Bitcoin Esplora, JSON-RPC EVM i ograniczenia.
- [Format sejfu](VAULT_FORMAT.md) — szyfrowanie, schematy v1/v2 i przechowywanie frazy odzyskiwania.
- [Model bezpieczeństwa](SECURITY_MODEL.md) — chronione zasoby, granice zaufania i ryzyka.
- [Roadmapa](ROADMAP.md) — funkcje działające i planowane.
- [Wyniki testów](TEST_RESULTS.md) — faktyczne wyniki lokalne i pominięte testy.

## Dokumentacja dla osób rozwijających projekt

- [Architektura](ARCHITECTURE.md) — podział pakietów i kierunek zależności.
- [Rozwój i testowanie](DEVELOPMENT.md) — środowisko oraz kontrole jakości.
- [Zasady współtworzenia](CONTRIBUTING.md) — changelog, commity i lista kontrolna wydania.
- [Polityka bezpieczeństwa](SECURITY.md) — zgłaszanie podatności.
- [Historia zmian](CHANGELOG.md) — zmiany w poszczególnych wersjach.

## Stan funkcji 0.6.0

- Zaszyfrowane lokalne sejfy i kopie zapasowe.
- Ograniczone tworzenie/odzyskiwanie portfela Bitcoin Mainnet BIP-39/BIP-84 offline.
- Odczyt salda i pierwszej strony historii pojedynczego adresu BTC przez jawnie wybrany endpoint Esplora.
- Odczyt natywnego salda przez JSON-RPC dla Ethereum, Polygon PoS, Arbitrum One, Optimism i Base.
- Każde zapytanie sieciowe wymaga `network_requests_enabled = true` oraz `--allow-network`.

Niezaimplementowane pozostają m.in. klucze i portfele EVM, tokeny ERC-20, Monero, historia EVM, odkrywanie wszystkich adresów, podpisywanie i wysyłanie transakcji oraz rzeczywisty transport Tor.
