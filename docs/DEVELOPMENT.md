# Development guide — Vaultsh 1.0.0-beta.1

## Install

Python 3.12+ is required. In a fresh clone:

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Test and lint

```bash
python -m compileall -q src tests
python -m pytest -q
python -m pytest --cov=vaultsh --cov-report=term-missing -q
ruff check .
mypy src/vaultsh
```

## Safety requirements for changes

- Use separate, chain-specific implementations; never share signing assumptions between BTC, EVM, Solana and Monero.
- Network clients must use explicit user-selected endpoints, bounded responses, timeouts, strict validation and no redirect/proxy fallback.
- New transfer paths must preview network, from/to address, amount, fee and total debit, then require typed confirmation. Never add unattended `--yes` broadcasting.
- Add official derivation/signing vectors and mocked tests. Live tests need separate opt-in, disposable wallets and tiny amounts; never put real keys/seeds in fixtures.
- Update README in English/Polish/Russian, `CHANGELOG.md`, matching docs and actual test results for each release.

This build's local validation did not reach real providers or broadcast a transaction. Seven tests are skipped when `textual`, `embit`, `eth-utils`, or `eth-account` dependencies cannot be imported. See `TEST_RESULTS.md`.
