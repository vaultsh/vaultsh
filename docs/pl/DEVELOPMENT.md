# Rozwój i testowanie

**🌐 Język:** [English](../DEVELOPMENT.md) · [Polski](DEVELOPMENT.md) · [Русский](../ru/DEVELOPMENT.md) · [README](../../README.pl.md)

## Wymagania

- Python 3.12 lub nowszy.
- `pip` i środowisko wirtualne.
- Połączenie z Internetem lub zaufane repozytorium pakietów na czas instalacji zależności.
- Git zalecany do przeglądania zmian i historii wydań.

## Przygotowanie środowiska

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS/Termux: source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Testy i kontrole jakości

```bash
pytest -q
pytest --cov=vaultsh --cov-report=term-missing -q
ruff check .
mypy src/vaultsh
git diff --check
```

Uruchamiaj tylko kontrole, których narzędzia są zainstalowane. Nie przedstawiaj nieuruchomionego Ruff/mypy/CI jako zaliczonego.

## Zasady testowania

- Preferuj deterministyczne testy jednostkowe i oficjalne wektory standardów.
- Klientom sieciowym wstrzykuj fałszywe transporty i odpowiedzi; testy nie powinny odpytywać publicznych API.
- Sprawdzaj odmowę połączenia bez obu zgód oraz gdy włączono Tor, którego transport nie istnieje.
- Testuj błędny JSON, niezgodne ID JSON-RPC/chain ID, nieprawidłowe ilości, duże odpowiedzi, przekierowania i przypadki brzegowe URL.
- Nigdy nie używaj prawdziwych fraz odzyskiwania, kluczy, sejfów użytkowników ani tokenów endpointów w fixtures.
- Nie opisuj salda jednego adresu jako pełnego salda portfela, dopóki nie ma odkrywania adresów i obsługi gap limit.

## Przed publikacją

Uruchom testy, formatowanie i analizę typów, przejrzyj `git diff`, sprawdź zależności/licencje, zaktualizuj README i changelog oraz odnotuj pominięte testy, nieweryfikowane platformy i niezrealizowane audyty.
