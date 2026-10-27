# Changelog

Wszystkie istotne zmiany w projekcie Vaultsh są dokumentowane w tym pliku.

Projekt znajduje się na etapie pre-alpha. Na tym etapie nie gwarantuje stabilności ani kompatybilności pomiędzy kolejnymi wersjami.

## \[MVP 0.1.0\] — Pierwsza wersja

Pierwsza wersja projektu Vaultsh, stanowiąca początkową implementację MVP (Minimum Viable Product).

### 🟩🟩🟩 Dodano

- Dodano plik `SECURITY.md` z wytycznymi dotyczącymi prywatnego zgłaszania podatności, obsługi sekretów i ograniczeń wersji pre-alpha.
- Dodano niezmienne ustawienia `AppConfig` z walidacją oraz loader konfiguracji TOML z bezpiecznymi wartościami domyślnymi.
- Dodano model `WalletSummary` zawierający niesekretne metadane portfela i podstawową walidację pól.
- Dodano wersjonowane, uwierzytelnione szyfrowanie danych bajtowych przy użyciu AES-256-GCM i Scrypt z biblioteki `cryptography`.
- Dodano ograniczoną walidację parametrów koperty szyfrowania przed uruchomieniem funkcji wyprowadzania klucza (KDF).
- Dodano atomowy zapis lokalnych plików oraz mechanizmy tworzenia i przywracania zaszyfrowanych kopii zapasowych skarbca.
- Dodano parser ścieżek derivacji zgodnych ze składnią BIP32. Parser analizuje wyłącznie ścieżki — nie wyprowadza kluczy prywatnych.
- Dodano minimalny protokół adaptera blockchaina bez zakładania, że reguły poszczególnych sieci są wzajemnie wymienne.
- Dodano jawne mechanizmy polityki dostępu do sieci oraz domyślnie wyłączone ustawienia telemetrii i połączeń sieciowych.
- Dodano opcjonalne narzędzia konfiguracji proxy Tor wykorzystujące adresy `socks5h://`, aby uniknąć lokalnego rozwiązywania DNS dla hostów docelowych przy użyciu zgodnego klienta.
- Dodano wielokrotnego użytku panele statusu `Rich` oraz jawne mechanizmy potwierdzania operacji.
- Rozszerzono CLI o polecenia wyświetlające status projektu, obsługiwane i planowane sieci, domyślne ustawienia prywatności oraz konfigurację.
- Dodano 48 testów jednostkowych obejmujących wyniki CLI, walidację i wczytywanie konfiguracji, szyfrowanie, przechowywanie skarbca, kopie zapasowe i ich przywracanie, ścieżki derivacji, politykę sieciową, konfigurację proxy Tor, metadane portfela oraz elementy interfejsu.

### 🟥🟥🟥 Usunięto

### Uwagi dotyczące bezpieczeństwa

- Vaultsh pozostaje projektem w fazie pre-alpha i nie nadaje się do przechowywania ani obsługi rzeczywistych środków.
- Tworzenie portfeli, generowanie i import fraz mnemonicznych, wyprowadzanie kluczy zgodnie z regułami konkretnych blockchainów, podpisywanie transakcji, pobieranie sald i rozgłaszanie transakcji nie zostały jeszcze zaimplementowane.
- Narzędzia Tor służą wyłącznie do opisu i konfiguracji proxy. Nie uruchamiają Tor, nie weryfikują połączenia i nie gwarantują anonimowości.

### Status wydania

- **Wersja:** `0.1.0`
- **Etap:** MVP / pre-alpha
- **Charakter wydania:** pierwsza wersja projektu
- **Stabilność:** brak gwarancji kompatybilności między wersjami
- **Gotowość produkcyjna:** niezalecana do obsługi rzeczywistych środków