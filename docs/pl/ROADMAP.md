# Roadmap — Vaultsh 1.0.0-beta.1

## W tej becie
- [x] Zaszyfrowany sejf i rekordy portfeli BTC/ETH/SOL.
- [x] QR/PNG rozpoznawanych publicznych adresów BTC/EVM/XMR/SOL.
- [x] BTC balance/history pojedynczego adresu i lokalnie podpisywana transakcja P2WPKH.
- [x] ETH Mainnet balance i lokalnie podpisywany transfer natywnego ETH (legacy EIP-155).
- [x] Solana Mainnet balance i lokalnie podpisywany transfer natywnego SOL.
- [x] Monero adres/saldo/portfel/wysyłanie przez oficjalny lokalny `monero-wallet-rpc`.
- [x] Jawne endpointy, podwójna zgoda na sieć i tekstowe potwierdzanie wysyłek.
- [x] Textual UI oraz README EN/PL/RU.

## Przed stabilnym wydaniem
- [ ] Ukończyć odkrywanie adresów BTC: receive/change indeksy, UTXO i testy odzyskiwania. **Nie wysyłaj prawdziwego BTC przed poprawką.**
- [ ] Uruchomić komplet oficjalnych wektorów derivacji/podpisu po instalacji wszystkich bibliotek.
- [ ] Testy integracyjne na własnych regtest/testnet/devnet; przetestować ponowne wysyłanie, awarie i stan potwierdzeń.
- [ ] ETH EIP-1559, tokeny ERC-20, historia i finality/receipt polling.
- [ ] SPL tokens, historia i finality polling Solany.
- [ ] Windows/Linux/Termux CI, Ruff, mypy, budowanie pakietu.
- [ ] Przegląd konfiguracji Monero RPC i odzyskiwania sejfu.
- [ ] Niezależny audyt kryptograficzny/bezpieczeństwa oraz kryteria stable release.
- [ ] Tor transport, hardware wallets, multisig i offline signing po osobnym projekcie i threat model.

`1.0.0-beta.1` nie jest produkcyjnym ani audytowanym portfelem.
