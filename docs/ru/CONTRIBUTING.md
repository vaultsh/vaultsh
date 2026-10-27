# Участие в разработке Vaultsh

**🌐 Язык:** [English](../../CONTRIBUTING.md) · [Polski](../pl/CONTRIBUTING.md) · [Русский](CONTRIBUTING.md)

## Проверки перед отправкой изменений

```bash
pytest --cov=vaultsh --cov-report=term-missing -q
ruff check .
mypy src/vaultsh
git diff --check
```

Не утверждайте, что проверка прошла, если её не запускали. Указывайте пропущенные тесты и непроверенные платформы.

## Формат changelog

Добавляйте изменения в `CHANGELOG.md` в раздел `## 🚧 [Unreleased]`, используя `### ✨ Added`, `### 🔄 Changed`, `### 🐛 Fixed`, `### 🔒 Security` и `### 🧪 Tests`. При выпуске переместите текст под заголовок версии с датой `YYYY-MM-DD`.

## Emoji для commit-сообщений

- `🔄 Update configuration handling` — изменение существующего поведения.
- `✨ Add encrypted vault storage` — новая функция.
- `🐛 Fix config validation` — исправление ошибки.
- `🔒 Harden encryption parameters` — безопасность.
- `⚡ Improve startup performance` — производительность.
- `📝 Update README` — документация.
- `♻️ Refactor network policy helpers` — рефакторинг без изменения поведения.
- `🧪 Add encryption unit tests` — тесты.
- `🔥 Remove deprecated module` — удаление функции.
- `🚀 Release Vaultsh 0.7.0` — релиз.

## Чек-лист pull request

- [ ] Сетевые запросы не включаются незаметно.
- [ ] Правила адресов, derivation, единиц и RPC остаются в адаптере соответствующей сети.
- [ ] Тесты покрывают корректные, ошибочные и вредоносные ответы без публичных API.
- [ ] В репозиторий не попали реальные фразы, ключи, пароли, хранилища или токены endpoint.
- [ ] Обновлены README, релевантная документация и changelog.
- [ ] `git diff --check` проходит, cache/артефакты исключены.
- [ ] Результаты описывают только реально выполненные проверки.
