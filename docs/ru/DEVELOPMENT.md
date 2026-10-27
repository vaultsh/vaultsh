# Разработка — Vaultsh 1.0.0-beta.1

Python 3.12+.

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

Держите логику BTC/EVM/SOL/XMR раздельной. Для сетевых клиентов обязательны явные endpoint, лимиты, таймауты и валидация. Отправка возможна только после обзора и точного подтверждения; не добавляйте `--yes`. Добавляйте официальные vectors, mocks и интеграционные тесты на собственных regtest/devnet. Не помещайте реальные seed/ключи в тесты или репозиторий. Для выпуска обновляйте README EN/PL/RU, CHANGELOG и фактический отчёт тестов.

Локально: 194 passed, 7 skipped, покрытие 53%. Нет реальных запросов/транзакций, Ruff/mypy, package build, CI и аудита.
