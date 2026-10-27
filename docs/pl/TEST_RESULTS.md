# Wyniki testów — Vaultsh 0.6.0 (bieżące drzewo kodu)

**🌐 Język:** [English](../TEST_RESULTS.md) · [Polski](TEST_RESULTS.md) · [Русский](../ru/TEST_RESULTS.md) · [README](../../README.pl.md)

## Środowisko lokalne

- System: kontener Linux.
- Python: `3.13.5`.
- pytest: `9.0.2`.
- pytest-cov: `7.0.0`.
- Polecenie: `pytest --cov=vaultsh --cov-report=term-missing -q`.
- Żadne publiczne zapytanie RPC/Esplora nie zostało wykonane; klienci sieciowi były testowane atrapami.

## Wynik

**144 testy zaliczone, 4 pominięte. Pokrycie linii: 82%.**

| Miara | Wynik |
|---|---:|
| Testy zaliczone | 144 |
| Testy pominięte | 4 |
| Mierzone instrukcje | 1400 |
| Pokryte instrukcje | 1141 |
| Niepokryte instrukcje | 259 |
| Łączne pokrycie | 82% |

W pięciu testach UI sprawdzono polski panel startowy i przegląd sieci, rosyjskie ekrany `about` i `privacy` oraz odrzucenie nieobsługiwanego kodu języka. Dotychczasowe testy obejmują też szyfrowanie, sejf, konfigurację, CLI, politykę sieciową, Bitcoin i profile EVM.

## Powód pominięcia testów

- Trzy testy wyprowadzania/odzyskiwania portfela Bitcoin wymagają biblioteki `embit`, której zabrakło w lokalnym środowisku.
- Jeden test sumy kontrolnej EIP-55 dla adresu mieszanego wymaga `eth-utils`, również niedostępnego lokalnie.

## Luki w weryfikacji

Ruff, mypy i budowanie pakietu nie zostały wykonane, jeśli narzędzia nie były dostępne. Nie potwierdzono hostowanego CI na Windows/Linux, zgodności Termux, działania z prawdziwymi endpointami ani niezależnego audytu bezpieczeństwa. Testy i pokrycie kodu nie są certyfikatem bezpieczeństwa.

## Odtworzenie wyniku

Zainstaluj zależności w zaufanym środowisku przez `python -m pip install -e ".[dev]"`, a następnie uruchom `pytest --cov=vaultsh --cov-report=term-missing -q`. W pełnym środowisku wszystkie testy zależne od `embit` i `eth-utils` powinny się wykonać zamiast zostać pominięte.
