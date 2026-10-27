# Interfejs Textual — Vaultsh 1.0.0-beta.1

Vaultsh ma pełnoekranowy interfejs Textual z czarno-pomarańczowym motywem, nagłówkiem/stopką, kartami oraz dashboardem Rich jako fallback dla wyjścia nieinteraktywnego. Wybór języka: `vaultsh --lang en`, `vaultsh --lang pl` lub `vaultsh --lang ru` przed komendą.

TUI oferuje status, podstawowe operacje sejfu/portfeli, wybór ścieżek lokalnych, ustawienia i formularze zapytań tylko do odczytu. **Wysyłanie transakcji odbywa się przez CLI:** `bitcoin send`, `ethereum send`, `solana send`, `monero send`.

Nagłówek pokazuje wersję, oczyszczoną nazwę lokalnego użytkownika oraz stan polityki/zapytania sieciowego — nie gwarantuje to łączności z Internetem. Wąski terminal przełącza siatkę na jedną kolumnę przez klasę CSS ustawianą w Pythonie; nieobsługiwane `@media` nie jest używane. Testów uruchomieniowych Textual nie wykonano w odizolowanym środowisku, bo brakowało biblioteki.
