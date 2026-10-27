# Contributing to Vaultsh

Vaultsh is security-sensitive beta software. Keep contributions small, reviewable, and supported by tests. Never claim that a mocked or dependency-skipped feature has been verified against a real network.

## Development setup

```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# Linux/macOS/Termux: source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m compileall -q src tests
python -m pytest --cov=vaultsh --cov-report=term-missing -q
ruff check .
mypy src/vaultsh
```

## Requirements for chain code

- Use chain-specific derivation/signing libraries; do not create one generic crypto path for Bitcoin, EVM, Solana and Monero.
- Prefer integer base units and strict decimal-string parsing for amounts. Never use floating point for transaction amounts/fees.
- Keep signing local. Prepare a transaction, show recipient/amount/network/fee, then require a typed confirmation before broadcast/relay. Do not add an unattended `--yes` broadcast flag.
- Keep secret phrases, private keys, signed raw transactions, RPC credentials and Monero transaction metadata out of logs, exceptions, dataclass reprs, README examples, fixtures and tests.
- Any new endpoint needs strict URL/network validation, timeouts, response-size limits, redirect handling, explicit network permission, and fake-response tests. Never automatically pick a public provider.
- Add tests using known official vectors for derivation/signing and mocked network responses. Mark tests as skipped when dependencies are unavailable, and record the reason instead of claiming success.
- Update README.md, README.pl.md, README.ru.md, CHANGELOG.md, docs/ and the release test report for user-visible changes.

## Commit message examples

- `✨ Add Solana native transfer preview`
- `🐛 Fix Monero Mainnet address validation`
- `🔒 Refuse unrecognized QR payloads`
- `🧪 Add transaction-signing regression tests`
- `📝 Update beta installation guide`
- `♻️ Refactor chain-specific wallet adapters`
- `🚀 Release Vaultsh 1.0.0-beta.1`

## Release checklist

1. Run tests with all runtime and dev dependencies installed.
2. Run official derivation/signing vectors and controlled local-node integration tests.
3. Build and inspect the wheel/sdist, audit dependencies/licenses, and test Windows/Linux/Termux.
4. Review all transaction previews and failure/cancellation paths, and verify no accidental broadcast occurs before typed confirmation.
5. Update version metadata, all three README files, changelog, security policy, test report, and release artifacts.
6. Do not label the project stable or safe for significant real funds without independent security review.
