# Textual interface — Vaultsh 1.0.0-beta.1

Vaultsh offers a Textual full-screen terminal UI with a black/orange theme, Header/Footer, tabbed task views and a Rich dashboard fallback when output is non-interactive. Select language with `vaultsh --lang en`, `vaultsh --lang pl`, or `vaultsh --lang ru` before a command.

The TUI provides a status overview, local encrypted-vault and wallet basics, public-address QR support where exposed, public read-only network queries, local path selection and non-secret settings. **Transaction sending is currently a CLI workflow** (`bitcoin send`, `ethereum send`, `solana send`, `monero send`) and is not a complete send wizard in the TUI.

The title reflects app version, sanitized local username and network permission/request status. It does not guarantee the terminal emulator's outer window title changes. Network states reflect policy/request state, not proof of Internet connectivity.

At narrow terminal widths, the overview grid toggles to a compact single-column layout via a Python-set CSS class; the CSS does not use unsupported `@media` syntax. Textual runtime tests could not run in the isolated build environment because the dependency was unavailable; test on your actual terminal before release.
