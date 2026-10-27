# Model bezpieczeństwa — Vaultsh 1.0.0-beta.1

Vaultsh beta nie był niezależnie audytowany. Nie trzymaj znacznych środków. Testy jednostkowe nie dowodzą bezpieczeństwa portfela.

- Sekrety BTC/ETH/SOL są w zaszyfrowanych rekordach sejfu. Fraza odzyskiwania daje kontrolę nad portfelem i może zostać przechwycona przez zrzut ekranu/log.
- Podpisy BTC/ETH/SOL powstają lokalnie, za pomocą oddzielnych bibliotek chain-specific. Monero jest obsługiwane przez lokalny `monero-wallet-rpc` i przechowuje klucze poza Vaultsh.
- Każde zdalne zapytanie wymaga jawnego endpointu, zezwolenia TOML i `--allow-network`; każda wysyłka wymaga przeglądu i dokładnego potwierdzenia tekstowego.
- RPC/Esplora może poznać publiczne adresy oraz metadane połączenia. Tor transport nie jest zaimplementowany.
- ETH send: natywne ETH Mainnet, legacy gasPrice. SOL send: tylko SOL. Monero zależy od prawidłowo skonfigurowanego lokalnego RPC/daemon.
- **BTC send nie jest bezpieczne dla realnych środków:** tylko pierwszy adres receive jest skanowany; zmiana `/1/0` nie jest odkrywana przez Vaultsh.
- QR rozpoznaje kształt adresu, ale nie jest pełnym walidatorem sum kontrolnych ani dowodem własności.
- Nie testowano rzeczywistego broadcastu. 7 testów pominięto przez zależności niedostępne offline; zob. `TEST_RESULTS.md`.
