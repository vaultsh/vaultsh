# Architektura — Vaultsh 1.0.0-beta.1

- `cli.py`: Typer komendy, przegląd operacji, dokładne tekstowe potwierdzenie przed broadcast/relay.
- `ui/`: Textual TUI, Rich fallback, EN/PL/RU, helpery QR/prompt.
- `crypto/`: Scrypt + AES-256-GCM oraz narzędzia derivacji.
- `storage/`: dokument sejfu, szyfrowane rekordy, backup/restore.
- `networks/bitcoin/`: BIP84, Esplora queries, ograniczony coin selection, lokalny podpis P2WPKH, broadcast.
- `networks/ethereum/`: JSON-RPC oraz lokalne podpisanie legacy EIP-155 tylko ETH Mainnet.
- `networks/solana/`: JSON-RPC Mainnet, native SOL, `solders`.
- `networks/monero/`: loopback-only klient oficjalnego `monero-wallet-rpc`; XMR wallet files/seed i podpis są zarządzane przez ten proces.
- `privacy/network_policy.py`: wymagane zezwolenie TOML plus `--allow-network`. Tor nie jest transportem zaimplementowanym.

Wysyłanie BTC/ETH/SOL: odczyt portfela z sejfu, zapytania do jawnego endpointu, budowa/podpis lokalny, podgląd adresu/kwoty/opłaty i exact typed confirmation, a dopiero potem broadcast. XMR: RPC przygotowuje transakcję bez relay; po potwierdzeniu przekazywane są metadane do `relay_tx`.

**Krytyczne ograniczenie BTC:** wyszukiwanie UTXO obejmuje tylko potwierdzone UTXO pierwszego adresu receive. Reszta trafia na `/1/0`, którego Vaultsh nie skanuje. Nie używaj wysyłania BTC z prawdziwymi środkami.
