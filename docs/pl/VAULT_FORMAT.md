# Format sejfu — Vaultsh 1.0.0-beta.1

Sejf jest eksperymentalnym lokalnym kontenerem, bez niezależnego audytu kryptograficznego/interoperacyjności. Zewnętrzna koperta wyprowadza klucz z hasła przy użyciu Scrypt i uwierzytelnia szyfrogram przez AES-256-GCM. Wewnątrz wersjonowany dokument przechowuje metadane i rekordy portfeli.

Frazy BIP-39 portfeli BTC/ETH/SOL znajdują się w uwierzytelnionym szyfrogramie; standardowe listowanie pokazuje tylko publiczne metadane. Pokazanie frazy wymaga dedykowanej komendy. Python nie gwarantuje wyzerowania sekretów z pamięci.

Monero jest oddzielne: seed i pliki XMR są przechowywane przez oficjalny `monero-wallet-rpc`, a nie w sejfie Vaultsh. Kopia zapasowa sejfu jest kopią zaszyfrowanych bajtów, nie zastępuje osobnej offline frazy i nie dowodzi możliwości odzyskania portfela.

Przed każdym zaufaniem: backup, próbne odtworzenie, weryfikacja adresów w drugim zgodnym portfelu i wektorów testowych. Nie traktuj testów jako audytu.
