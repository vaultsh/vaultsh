# Polityka bezpieczeństwa

**🌐 Język:** [English](../../SECURITY.md) · [Polski](SECURITY.md) · [Русский](../ru/SECURITY.md)

## Zgłaszanie podatności

Nie publikuj niezałatanej podatności wraz z danymi umożliwiającymi wykorzystanie. Zgłoszenie powinno zawierać:

- wersję/commit, system operacyjny i wersję Pythona;
- zwięzły opis wpływu oraz odtwarzalne kroki z użyciem danych syntetycznych;
- informację, czy problem dotyczy poufności, integralności, prywatności sieci, dostępności czy pakowania;
- proponowane ograniczenie ryzyka, jeżeli jest znane.

Nie dołączaj prawdziwych fraz odzyskiwania, prywatnych kluczy, haseł, plików sejfu, kopii zapasowych ani sekretów endpointów.

## Zakres i ograniczenia

Vaultsh jest projektem pre-alpha i nie był niezależnie audytowany. Wyniki testów nie są certyfikatem bezpieczeństwa. Python nie gwarantuje wyzerowania sekretów w pamięci. Fraza odzyskiwania jest wyświetlana w terminalu i może zostać przechwycona przez nagranie lub zrzut ekranu. Wyniki salda/historii są dostarczane przez endpoint i nie są niezależnie weryfikowanym dowodem kryptograficznym.
