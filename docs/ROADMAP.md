# Roadmap — Vaultsh 1.0.0-beta.1

## Implemented in this beta
- [x] Encrypted local vault and wallet records for BTC/ETH/SOL.
- [x] Public-address QR display/PNG export for recognizable BTC/EVM/XMR/SOL formats.
- [x] BTC one-address balance/history and locally signed P2WPKH sends after review.
- [x] ETH Mainnet native balance and locally signed legacy EIP-155 sends.
- [x] Native SOL balance and locally signed native SOL sends.
- [x] Monero wallet management/address/balance/send delegated to official local `monero-wallet-rpc`.
- [x] Explicit endpoint selection, double opt-in network permission and typed send confirmation.
- [x] Black/orange Textual UI, EN/PL/RU documentation and CLI translations.

## Required before stable release
- [ ] Fix Bitcoin wallet discovery: scan receive/change indexes, handle multiple UTXOs, test UTXO conflicts and recoverability. **Do not send real BTC until done.**
- [ ] Full dependency-installed derivation/signing vector runs, including official vectors and independent wallet interoperability.
- [ ] Live integration testing against self-hosted regtest/devnet/testnet nodes; test signing and failure/rebroadcast states.
- [ ] Receipt/finality polling and robust confirmation state for ETH/SOL.
- [ ] EIP-1559 transaction support, token balances/transfers, Solana SPL tokens, wallet-wide history/address gap discovery.
- [ ] Automated Windows, Linux and Termux CI; Ruff/mypy and package build.
- [ ] Monero RPC/daemon setup checks, restore procedure and adversarial configuration review.
- [ ] Independent cryptographic/security audit and documented stable-release criteria.
- [ ] Evaluate actual Tor transport, hardware wallets, multisig and offline signing only after threat-model/design review.

## Release status

`1.0.0-beta.1` is a pre-stable beta, not a production-ready wallet. Local tests are mocked and do not prove that real transfers succeed safely.
