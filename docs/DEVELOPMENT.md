# Development and testing

This page describes the local workflow for Vaultsh contributors. The project targets Python 3.12+ and uses a `src/` layout.

## Environment setup

From the project root:

```bash
python -m venv .venv
```

Activate the environment, then install the project and development dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Windows PowerShell activation:

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux/macOS/Termux-style activation:

```bash
source .venv/bin/activate
```

The editable installation exposes the `vaultsh` console script. `python -m vaultsh` is also intended to start the CLI.

## Tests

Run all tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=vaultsh --cov-report=term-missing
```

Tests should use temporary directories, deterministic public test vectors, fake prompts where feasible, and synthetic secrets only. Never include genuine recovery phrases or wallet data in fixtures.

The BIP-84 address-vector test depends on `embit`. Install all project dependencies before interpreting skipped wallet tests as a successful complete run. A test skipped because a dependency is missing is not a pass for that feature.

## Static checks

```bash
ruff check .
mypy src/vaultsh
```

Also review the changed lines and whitespace:

```bash
git diff --check
git status --short
git diff
```

A local test run does not replace CI on each supported platform. Windows, Linux, and Termux need separate compatibility verification before being claimed as tested targets.

## Tests by subsystem

- `test_cli.py`: user-facing command behavior, prompts, exit codes, and output safety.
- `test_config.py`: TOML parsing, type checks, ranges, and privacy defaults.
- `test_encryption.py`: envelope round-trip, authentication failure, and malformed headers/KDF parameters.
- `test_vault.py` and `test_vault_document.py`: file safety, document validation, schema support, and migrations.
- `test_wallet_store.py`: record persistence, duplicate rejection, and secret redaction from public summaries.
- `test_bitcoin_wallet.py`: BIP-39 validity and authoritative BIP-84 derivation test vectors.
- `test_derivation.py`: parsing only; this module does not derive private keys.
- `test_network_policy.py` and `test_tor.py`: policy decisions and proxy-setting validation; they do not prove live networking or anonymity.

## Safe change principles

- Do not implement a custom hash, cipher, mnemonic word list, elliptic-curve operation, or transaction-signing primitive when a well-maintained standard library is appropriate.
- Keep network access opt-in and independently tested. No background network activity or telemetry should be introduced implicitly.
- Keep chain-specific logic isolated per adapter.
- Add failure-path tests, schema compatibility tests, and authoritative vectors for cryptographic behavior.
- Update README, the detailed docs, SECURITY.md, and CHANGELOG.md when relevant.
- Bump version metadata in both `pyproject.toml` and `src/vaultsh/__init__.py` when preparing a release.

## Build/package check

The project uses Hatchling. To verify that the package builds, install the build frontend and run:

```bash
python -m pip install build
python -m build
```

Review the contents of `dist/` before distributing an artifact. Do not package local vaults, backups, environment files, test caches, or credentials.
