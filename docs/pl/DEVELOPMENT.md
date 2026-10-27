# Rozwój — Vaultsh 1.0.0-beta.1

Wymagany Python 3.12+.

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m compileall -q src tests
python -m pytest --cov=vaultsh --cov-report=term-missing -q
ruff check .
mypy src/vaultsh
```

Zasady: osobne logiki BTC/EVM/SOL/XMR; endpointy jawne, limity/timeouty/walidacja; wysyłka wyłącznie po podglądzie i typed confirmation; brak `--yes` dla broadcastu; oficjalne wektory, mock tests oraz testy integracyjne z własnym regtest/devnet. Nigdy nie dodawaj prawdziwych kluczy/seedów do testów ani repozytorium. Aktualizuj README EN/PL/RU, CHANGELOG i raport wyników tylko wynikami faktycznie wykonanych kontroli.

W tym środowisku lokalnie: 194 zaliczone, 7 pominiętych, 53% pokrycia. Brak live-network/real-broadcast, Ruff/mypy, package build, Windows/Linux CI i audytu. Zob. `TEST_RESULTS.md`.
