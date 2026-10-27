# Security Policy

**Vaultsh 1.0.0-beta.1 is beta software and has not received an independent security audit. Do not use it to store or transact significant funds.** Transaction broadcasts on public mainnets are irreversible.

## Reporting a vulnerability

Do not publish recovery phrases, private keys, vault files, RPC credentials, provider URLs containing access tokens, signed raw transactions, Monero transaction metadata, or other secrets in a public issue. Provide a minimal reproduction with synthetic keys, fake endpoints, and sanitized logs. If a private reporting channel is configured for the repository, use it; otherwise open a public issue without secrets asking for a private disclosure path.

## Implemented security boundaries

- The local Vaultsh vault uses authenticated encryption and password-derived keys. BTC/ETH/SOL BIP-39 phrases are stored inside the encrypted payload; wallet listing shows only public metadata.
- Monero secrets are handled by the official local `monero-wallet-rpc` and stored in the Monero wallet directory, not inside the Vaultsh vault.
- Network commands require both `network_requests_enabled = true` in TOML and the command-line flag `--allow-network`.
- Remote Esplora/EVM/Solana endpoints must use HTTPS; redirects and ambient proxy discovery are disabled by those clients. HTTP is limited to loopback for local services.
- Monero wallet RPC is restricted to loopback and validates addresses as Mainnet before transfer preparation/display.
- Transfers show amount, recipient, and fee information and require exact typed confirmation. The CLI intentionally has no `--yes` bypass.
- QR generation accepts only recognizable public address formats and rejects whitespace/mnemonic text and unrecognized payloads. It is not a full checksum validator for every chain.

## Important limitations

- **Bitcoin sending has a known funds-discovery limitation:** only the first receive address is scanned for spendable UTXOs; change is sent to BIP-84 change path `/1/0`, which this release does not scan. Do not use the BTC send path with real funds until change/address discovery is implemented and verified.
- Ethereum sends native ETH on Mainnet only, using a legacy `gasPrice` transaction; other EVM profiles are balance-only.
- Solana sends native SOL only; a JSON-RPC signature response does not prove confirmation/finality.
- Monero depends on the user's local wallet-RPC and daemon configuration. Never bind `monero-wallet-rpc` to a public interface.
- Tor transport, hardware-wallet support, multisig, complete wallet address discovery, token transfers, and independent audit are not implemented.
- No live endpoint or real transaction was used in the build/test environment. Some tests were skipped because required chain/UI dependencies were unavailable.

## User responsibilities

Keep recovery phrases offline. Protect the vault password and recovery phrase independently. Back up and test restoring both the Vaultsh vault and Monero wallet files. Treat data from remote providers as untrusted. Review the destination, amount, network and maximum fee at each transaction prompt. Verify the resulting transaction using a separate trusted node/explorer.
