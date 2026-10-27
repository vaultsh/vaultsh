# Changelog — Vaultsh

## 🚀 [1.0.0-beta.1] — 2026-10-27

### ✨ Dodano
- Portfele Bitcoin, Ethereum Mainnet i Solana tworzone/odzyskiwane z angielskiej frazy BIP-39 oraz zaszyfrowane rekordy BTC/ETH/SOL.
- Lokalne podpisywanie i wysyłanie P2WPKH BTC, natywnego ETH (legacy EIP-155) i natywnego SOL po podglądzie i dokładnym potwierdzeniu tekstowym.
- Operacje Monero przez oficjalny lokalny `monero-wallet-rpc`; przygotowanie transferu bez relay, a następnie relay po potwierdzeniu.
- QR/PNG dla rozpoznawanych publicznych adresów BTC/EVM/XMR/SOL.
- Komendy i testy wysyłania, walidacji kwot, adresów, mainnet i metadata relay XMR.

### 🔄 Zmieniono
- Wersja pakietu to `1.0.0b1` (etykieta `1.0.0-beta.1`). Dokumentację i interfejs uaktualniono w językach EN/PL/RU.

### 🧪 Testy
- Lokalnie: **194 zaliczone, 7 pominiętych, 53% pokrycia**.
- Pominięcia: Textual (1), embit (4), eth-utils (1), eth-account (1). Nie wykonano połączeń z prawdziwymi RPC/Esplora ani broadcastu realnej transakcji.

### 🛡️ Ograniczenia bezpieczeństwa
- **Nie używaj BTC send z prawdziwymi środkami**: UTXO wyszukiwane są tylko na pierwszym receive-adresie, a change `/1/0` nie jest wykrywany przez Vaultsh.
- ETH send obejmuje wyłącznie natywny ETH Mainnet w formacie legacy. SOL send obejmuje tylko natywny SOL. Monero korzysta z zewnętrznego procesu `monero-wallet-rpc`, który musi działać lokalnie i bezpiecznie.
- Nie ma audytu, transportu Tor, multisig, hardware wallet ani testów realnych broadcastów.

## 🚧 Unreleased
Brak zapisanych zmian.
