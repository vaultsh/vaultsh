# Polityka bezpieczeństwa — Vaultsh 1.0.0-beta.1

Vaultsh to wersja beta bez niezależnego audytu. Nie przechowuj znacznych środków. Jeśli zgłaszasz błąd, nie dołączaj fraz, kluczy, sejfów ani URL-i RPC zawierających tokeny.

## Granice bezpieczeństwa
- Frazy BTC/ETH/SOL przechowywane są w zaszyfrowanym sejfie, ale podczas tworzenia/odzyskiwania są wyświetlane w terminalu.
- Monero jest zarządzane przez oficjalny lokalny `monero-wallet-rpc`; seed i pliki XMR nie znajdują się w sejfie Vaultsh.
- Każda operacja sieciowa wymaga jawnego endpointu, zezwolenia TOML i `--allow-network`.
- Wysyłka wymaga przeglądu sieci, odbiorcy, kwoty, opłaty i dokładnego tekstowego potwierdzenia.
- Transport Tor nie jest zaimplementowany; aplikacja nie może twierdzić, że ruch jest anonimizowany.

## Znane ryzyka
- **Nie wysyłaj prawdziwego BTC:** wykrywane są tylko potwierdzone UTXO pierwszego adresu receive; zmiana trafia na `/1/0`, którego Vaultsh jeszcze nie skanuje.
- ETH to wyłącznie ETH Mainnet i transakcje legacy; SOL to wyłącznie natywne SOL. Brak tokenów, multisig i sprzętowych kluczy.
- Monero RPC i daemon muszą być poprawnie skonfigurowane i dostępne tylko przez loopback.
- QR rozpoznaje kształt adresu, ale nie potwierdza własności i nie jest uniwersalnym walidatorem checksum.
- Testy są lokalne i używają mocków. Nie przetestowano realnego broadcastu ani niezależnie nie zbadano kryptografii.

Zgłoszenia podatności przekazuj prywatnie maintainerom projektu, bez publikowania szczegółów exploita przed ustaleniem poprawki. Nie traktuj wyników testów jako audytu.
