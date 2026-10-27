# Adaptery sieciowe — Vaultsh 1.0.0-beta.1

| Sieć | Odczyt | Wysyłanie | Ograniczenie |
|---|---|---|---|
| Bitcoin Mainnet | Saldo i pierwsza strona historii jednego adresu przez Esplora | Podpis lokalny P2WPKH i broadcast | **Nie używaj prawdziwych środków:** skanowany jest tylko pierwszy adres odbiorczy; zmiana na `/1/0` nie jest odkrywana |
| Ethereum Mainnet (chain ID 1) | Saldo ETH przez JSON-RPC | Lokalnie podpisane legacy EIP-155 | Bez EIP-1559, ERC-20, kontraktów i potwierdzeń/finality |
| Polygon (137), Arbitrum One (42161), Optimism (10), Base (8453) | Salda aktywów natywnych | Wysyłanie wyłączone | Tylko odczyt |
| Solana Mainnet Beta | Saldo SOL, weryfikacja genesis hash | Lokalnie podpisany transfer SOL | Bez SPL, historii, discovery i finality polling |
| Monero Mainnet | Adres/saldo przez lokalny oficjalny RPC | RPC przygotowuje nieprzekazaną transakcję; potwierdzenie; następnie relay | Seed i pliki portfela pozostają poza sejfem Vaultsh; RPC wyłącznie loopback |

## Polityka sieciowa

Każda operacja wymaga jawnego endpointu, `network_requests_enabled = true` w TOML i flagi `--allow-network`. Tor nie jest zaimplementowany; przy `tor_enabled=true` operacja kończy się odmową. Operator endpointu może poznać sprawdzany publiczny adres i metadane połączenia. Testy sieciowe używają atrap; w środowisku przygotowującym wydanie nie broadcastowano prawdziwej transakcji.

## Bitcoin

Saldo/historia dotyczą pojedynczego adresu. Wysyłanie wybiera potwierdzone UTXO pierwszego adresu, szacuje opłatę, podpisuje P2WPKH lokalnie i wymaga dokładnego potwierdzenia przed POST `/tx`. Reszta trafia na `m/84'/0'/0'/1/0`, którego Vaultsh jeszcze nie skanuje. Środki są możliwe do odzyskania z frazy w zgodnym portfelu, ale Vaultsh nie umie ich obecnie wykryć/spendować.

## Ethereum i Solana

ETH: sprawdzenie chain ID, podpis legacy `gasPrice` na Mainnet, limit opłaty i potwierdzenie przed `eth_sendRawTransaction`. Hash odpowiedzi to zgłoszenie, nie finalność. SOL: endpoint weryfikowany przez genesis hash Mainnet; kwoty w lamportach; podpisany transfer SOL wysyłany po potwierdzeniu. SPL i finality polling nie istnieją.

## Monero

Połączenie tylko z `monero-wallet-rpc` na loopback. Adres portfela i cel muszą być Mainnet. Transfer używa `do_not_relay=true` i `get_tx_metadata=true`; po pokazaniu kwoty/opłaty oraz tekstowym potwierdzeniu Vaultsh wywołuje `relay_tx` z metadanymi przygotowanej transakcji. Zweryfikuj konfigurację demona i RPC.
