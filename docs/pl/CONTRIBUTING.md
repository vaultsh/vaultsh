# Współtworzenie Vaultsh

**🌐 Język:** [English](../../CONTRIBUTING.md) · [Polski](CONTRIBUTING.md) · [Русский](../ru/CONTRIBUTING.md)

## Kontrole przed zgłoszeniem zmian

```bash
pytest --cov=vaultsh --cov-report=term-missing -q
ruff check .
mypy src/vaultsh
git diff --check
```

Nie twierdź, że narzędzie przeszło, jeśli go nie uruchomiono. Opisuj liczbę pominiętych testów i niezweryfikowane platformy.

## Format changeloga

W `CHANGELOG.md` dopisuj zmiany do `## 🚧 [Unreleased]`, z nagłówkami `### ✨ Added`, `### 🔄 Changed`, `### 🐛 Fixed`, `### 🔒 Security` i `### 🧪 Tests`. Przy wydaniu przenieś treść do numeru wersji z datą `YYYY-MM-DD`.

## Emoji w commitach

- `🔄 Update configuration handling` — zmiana istniejącej funkcji.
- `✨ Add encrypted vault storage` — nowa funkcja.
- `🐛 Fix config validation` — naprawa błędu.
- `🔒 Harden encryption parameters` — zmiana związana z bezpieczeństwem.
- `⚡ Improve startup performance` — wydajność.
- `📝 Update README` — dokumentacja.
- `♻️ Refactor network policy helpers` — refaktoryzacja bez zamierzonej zmiany funkcji.
- `🧪 Add encryption unit tests` — testy.
- `🔥 Remove deprecated module` — usunięcie funkcji.
- `🚀 Release Vaultsh 0.7.0` — wydanie.

## Lista kontrolna pull requestu

- [ ] Nie włączono po cichu ruchu sieciowego.
- [ ] Zasady adresów, derivacji, jednostek i RPC pozostają w adapterze danej sieci.
- [ ] Testy obejmują dane poprawne, błędne i złośliwe bez publicznych API.
- [ ] Nie dodano prawdziwych fraz, kluczy, haseł, sejfów ani tokenów endpointów.
- [ ] Zaktualizowano odpowiednie README, dokumentację i changelog.
- [ ] `git diff --check` przechodzi, a cache i artefakty są ignorowane.
- [ ] Opis wyników jest zgodny z faktycznie wykonanymi kontrolami.
