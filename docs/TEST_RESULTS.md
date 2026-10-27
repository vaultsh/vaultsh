# Test results — Vaultsh 0.6.0 (current working tree)

This report records the actual local test run completed on **2026-10-27**. These results are not a security certification and do not replace platform CI or independent review.

## Local environment

- OS: Linux container.
- Python: `3.13.5`.
- pytest: `9.0.2`.
- pytest-cov: `7.0.0`.
- Command: `pytest --cov=vaultsh --cov-report=term-missing -q`.
- Live public RPC/Esplora requests: none. Network-client tests use fake openers and synthetic responses.

## Result

**144 passed, 4 skipped. Measured line coverage: 82%.**

| Measure | Result |
|---|---:|
| Tests passed | 144 |
| Tests skipped | 4 |
| Total statements measured | 1,400 |
| Statements covered | 1,141 |
| Statements missed | 259 |
| Aggregate line coverage | 82% |

Five UI-language regression tests cover the Polish dashboard and network overview, Russian `about` and privacy screens, and invalid language handling. The expanded test suite includes parameterized checks for all five supported EVM profile IDs/assets, an EVM CLI test selecting Polygon, and existing Bitcoin balance/history, vault, encryption, config, CLI, and privacy-policy tests. The CLI and network tests use synthetic responses; they do not contact public RPC providers.


## Why tests were skipped

- Three Bitcoin wallet derivation/recovery tests require `embit`, which was not installed in the local environment.
- One EVM mixed-case EIP-55 checksum test requires `eth-utils`, which was not installed locally.

An attempt to install the missing packages failed because package-index DNS/network access was unavailable in this environment. The project declares these as runtime dependencies, and the `.github/workflows/tests.yml` workflow installs the full package before testing. The workflow has been added, but a hosted Windows/Linux run has not been observed in this session; do not treat it as a passing CI result.

The four skipped tests mean this local run did **not** execute the complete BIP-39/BIP-84 derivation checks or mixed-case EIP-55 checksum validation. The test code is present and should run after installing all dependencies.

## Important verification gaps

- Ruff and mypy were not run; those tools were not installed in the local environment.
- `python -m build` was not run locally; the `build` package was not available and package-index access failed.
- Windows, Linux distributions outside this container, and Android/Termux compatibility were not verified.
- No live RPC endpoint was contacted. Provider interoperability, TLS behavior against real servers, and live chain state were not tested.
- No independent cryptographic or application security audit was performed.

## Reproducing the result

Install the project and all test dependencies in a fresh environment:

```bash
python -m pip install -e ".[dev]"
pytest --cov=vaultsh --cov-report=term-missing -q
```

After all dependencies are installed, expect the dependency-gated tests to run rather than skip. Update this file whenever a new release or test run materially changes the results, and preserve the actual environment and limitations.
