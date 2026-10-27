# Adaptery sieciowe

**🌐 Język:** [English](../NETWORK_ADAPTERS.md) · [Polski](NETWORK_ADAPTERS.md) · [Русский](../ru/NETWORK_ADAPTERS.md) · [README](../../README.pl.md)

## Obsługiwane sieci

| Klucz | Sieć | Chain ID | Aktywo | Dostępne operacje |
|---|---|---:|---|---|
| `bitcoin` | Bitcoin Mainnet | — | BTC | Saldo jednego adresu i pierwsza strona historii przez API Esplora |
| `ethereum` | Ethereum Mainnet | `1` | ETH | Natywne saldo przez JSON-RPC 2.0 |
| `polygon` | Polygon PoS Mainnet | `137` | POL | Natywne saldo przez JSON-RPC 2.0 |
| `arbitrum` | Arbitrum One | `42161` | ETH | Natywne saldo przez JSON-RPC 2.0 |
| `optimism` | Optimism Mainnet | `10` | ETH | Natywne saldo przez JSON-RPC 2.0 |
| `base` | Base Mainnet | `8453` | ETH | Natywne saldo przez JSON-RPC 2.0 |
| `monero` | Monero | — | — | Niezaimplementowane |

## Model zezwoleń

Każda operacja sieciowa wymaga `network_requests_enabled = true` w TOML i `--allow-network`. Nie ma automatycznego wyboru dostawcy. Zdalny endpoint musi używać HTTPS; HTTP jest dozwolone wyłącznie na loopback. Klienci stosują timeouty, limity rozmiaru odpowiedzi, odrzucają przekierowania i ignorują automatyczne proxy.

## Bitcoin Mainnet / Esplora

Saldo i historia dotyczą tylko adresu podanego przez użytkownika. Historia obejmuje pierwszą stronę i najwyżej 25 rekordów — nie jest pełną historią portfela i nie wyszukuje innych adresów. Wynik jest dostarczony przez endpoint, a nie niezależnie zweryfikowany jako dowód stanu.

## EVM JSON-RPC

Przed `eth_getBalance` program porównuje `eth_chainId` z profilem:

| `--chain` | Oczekiwany ID | Jednostka wyświetlania |
|---|---:|---|
| `ethereum` | `0x1` (1) | ETH / wei |
| `polygon` | `0x89` (137) | POL / jednostki bazowe |
| `arbitrum` | `0xa4b1` (42161) | ETH / wei |
| `optimism` | `0xa` (10) | ETH / wei |
| `base` | `0x2105` (8453) | ETH / wei |

Wartości są przetwarzane jako liczby całkowite. Odpowiedź dostawcy nie jest dowodem stanu. Mieszane wielkości liter w adresie wymagają poprawnej sumy EIP-55.

## Jawne ograniczenia

Nie ma tworzenia/odzyskiwania portfela EVM, przechowywania kluczy EVM, tokenów ERC-20, historii transakcji EVM, wywołań kontraktów poza opisanym odczytem salda, estymacji gas, podglądu, podpisywania ani wysyłania transakcji. Akceptowane są tylko wymienione mainnety. Monero ma odrębny model kluczy i prywatności — nie można traktować go jako odmiany Bitcoin/EVM. Katalog lub protokół adaptera nie oznacza kompletnej obsługi sieci.
