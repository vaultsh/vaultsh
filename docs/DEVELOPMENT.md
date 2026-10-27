# Development and testing

This guide describes the local workflow for Vaultsh **0.6.0**. A passing test suite is useful evidence, not a security certification.

## Requirements

- Python 3.12 or newer.
- `pip` and a virtual environment.
- Internet access or a trusted package mirror for installing project dependencies.
- Git is recommended for reviewing diffs and release history.

## Set up the environment

From the repository root:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS/Termux: source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

The runtime dependencies include Typer, Rich, cryptography, `embit`, `eth-utils`, and `eth-hash[pycryptodome]`. The development extra contains pytest, pytest-cov, Ruff, and mypy.

## Run tests

```bash
pytest -q
pytest --cov=vaultsh --cov-report=term-missing
```

Tests use fake HTTP openers and synthetic JSON-RPC/Esplora responses. They do not need a running node and should not access live endpoints. Bitcoin derivation tests require `embit`; EVM mixed-case EIP-55 checksum tests require `eth-utils` with a Keccak backend. Install project dependencies before expecting those tests to run instead of skip.

## Quality checks

```bash
ruff check .
ruff format --check .
mypy src/vaultsh
python -m compileall -q src tests
python -m build
```

The local result report lives in [TEST_RESULTS.md](TEST_RESULTS.md). It records the actual environment and any skipped tests; it must be regenerated after code/dependency changes. Do not replace missing tooling with claims of success.

## Test design

- Prefer deterministic unit tests and official standard vectors for derivation/checksum logic.
- Inject fake openers into network clients rather than querying public services during tests.
- Verify network commands fail closed when config permission or `--allow-network` is missing, and when Tor is requested but unavailable.
- Test malformed response JSON, wrong JSON-RPC IDs, incorrect chain IDs, invalid quantities, oversized responses, redirects, and endpoint URL edge cases.
- Never use real recovery phrases, live private keys, live vault files, or user data in fixtures.
- Do not assert that an address balance is a complete wallet balance unless address discovery and gap-limit handling have actually been implemented.

## Before publishing a release

1. Update `__version__`, `pyproject.toml`, `CHANGELOG.md`, README, and all affected docs together.
2. Install all project dependencies and run the complete test suite, ensuring tests did not silently skip key vectors.
3. Run Ruff, mypy, the package build, and the OS/Python matrix CI.
4. Inspect `git diff --check`, `git status --short`, archive contents, and dependency changes.
5. Confirm the archive excludes caches, `.coverage`, secrets, vault files, backups, and local config.
6. Document failures, skips, unverified environments, and unresolved security issues explicitly.
7. Never imply the application is suitable for real funds without independent review and documented release gates.
