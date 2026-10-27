# Wyniki testów — Vaultsh 1.0.0-beta.1

Ostatni lokalny test na Linux, Python 3.13.5, 2026-10-27:

**194 passed, 7 skipped; pokrycie instrukcji 53% (1577/2986).**

Pominięto 7 testów z powodu brakujących zależności w offline środowisku: Textual (1), embit (4), eth-utils (1), eth-account (1). `python -m compileall -q src tests` przechodzi. Pomoc CLI sprawdzono dla root, wallet, BTC send, ETH send, SOL send, Monero send i QR.

Testy RPC/Esplora używają atrap. **Nie łączono się z publicznym endpointem i nie broadcastowano prawdziwej transakcji.** Nie uruchomiono Ruff, mypy, budowania wheel, CI na Windows/Linux/Termux ani niezależnego audytu. Pokrycie kodu nie jest miarą bezpieczeństwa; moduły podpisywania mają niskie pokrycie.

Powtórzenie po instalacji wszystkich zależności:
```bash
python -m pip install -e ".[dev]"
python -m compileall -q src tests
python -m pytest --cov=vaultsh --cov-report=term-missing -q
ruff check .
mypy src/vaultsh
```
