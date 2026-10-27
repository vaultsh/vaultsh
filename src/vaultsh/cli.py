"""Vaultsh command-line interface.

The CLI provides encrypted vault management, offline Bitcoin Mainnet wallet
creation/recovery, and an explicitly authorized read-only Esplora balance lookup.
It does not sign transactions or broadcast payments.
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table

from vaultsh import __version__
from vaultsh.config import AppConfig, ConfigError, load_config
from vaultsh.networks.base import NetworkError
from vaultsh.networks.bitcoin.client import BitcoinEsploraClient, format_btc
from vaultsh.networks.bitcoin.wallet import generate_mnemonic
from vaultsh.privacy.network_policy import NetworkAccessDenied, require_network_access
from vaultsh.storage.backup import create_backup, restore_backup
from vaultsh.storage.vault_document import (
    MIN_VAULT_PASSWORD_LENGTH,
    create_vault_document,
    read_vault_document,
)
from vaultsh.storage.wallet_store import add_bitcoin_wallet, get_recovery_phrase, list_wallets

app = typer.Typer(
    name="vaultsh",
    help="Privacy-focused, self-custodial multi-chain wallet (pre-alpha).",
    no_args_is_help=False,
    add_completion=False,
)

vault_app = typer.Typer(
    name="vault",
    help="Create, verify, back up, and restore local encrypted vault containers.",
    no_args_is_help=True,
)
app.add_typer(vault_app, name="vault")
wallet_app = typer.Typer(
    name="wallet",
    help="Create, recover, and list offline Bitcoin Mainnet wallets.",
    no_args_is_help=True,
)
app.add_typer(wallet_app, name="wallet")
bitcoin_app = typer.Typer(
    name="bitcoin",
    help="Read-only Bitcoin Mainnet queries using an explicitly selected Esplora endpoint.",
    no_args_is_help=True,
)
app.add_typer(bitcoin_app, name="bitcoin")
console = Console()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Show a landing screen when no command is supplied."""
    if ctx.invoked_subcommand is not None:
        return

    table = Table(show_header=False, box=None, pad_edge=False)
    table.add_row("[bold cyan]about[/]          Project status and limitations")
    table.add_row("[bold cyan]vault init[/]     Create an encrypted empty vault")
    table.add_row("[bold cyan]vault check[/]    Verify/decrypt a vault metadata document")
    table.add_row("[bold cyan]vault backup[/]   Back up an encrypted vault")
    table.add_row("[bold cyan]vault restore[/]  Restore an encrypted backup")
    table.add_row("[bold cyan]wallet create[/]  Create a Bitcoin Mainnet wallet")
    table.add_row("[bold cyan]wallet recover[/] Recover a wallet from a BIP-39 phrase")
    table.add_row("[bold cyan]wallet list[/]    List public wallet details in a vault")
    table.add_row("[bold cyan]bitcoin balance[/] Read address balance via explicit Esplora API")
    table.add_row("[bold cyan]networks[/]       Supported and planned adapters")
    table.add_row("[bold cyan]privacy[/]        Privacy defaults")
    table.add_row("[bold cyan]config[/]         Default non-secret configuration")
    console.print(
        Panel(
            table,
            title=f"[bold cyan]VAULTSH[/] [dim]v{__version__}[/]",
            subtitle="[dim]Private · Self-custodial · Terminal-native[/]",
            border_style="cyan",
        )
    )
    console.print(
        "[yellow]PRE-ALPHA:[/] Offline Bitcoin wallet derivation and explicitly authorized "
        "read-only balance lookup are available. Transaction signing and broadcasting are "
        "not implemented; do not use this build for real funds."
    )
    console.print("Run [cyan]vaultsh --help[/] to see commands.")


@app.command()
def about() -> None:
    """Display project scope and current implementation status."""
    message = "\n\n".join(
        [
            "Vaultsh is a Python-first, privacy-focused multi-chain wallet project.",
            "Implemented: encrypted vaults and backups, Bitcoin Mainnet BIP-39 phrase "
            "generation/recovery, first BIP-84 Native SegWit receiving-address derivation, "
            "and encrypted wallet-record storage. A read-only balance lookup is available "
            "through a user-selected Esplora-compatible endpoint when networking is explicitly "
            "enabled.",
            "Not implemented: address-gap discovery, transaction construction/signing/"
            "broadcasting, Ethereum, or Monero. The balance lookup sends the address to the "
            "chosen endpoint.",
            "This pre-alpha build is not suitable for real funds.",
        ]
    )
    console.print(Panel(message, title="About Vaultsh", border_style="cyan"))


@app.command()
def networks() -> None:
    """Show planned network integrations and their status."""
    table = Table(title="Network adapter roadmap")
    table.add_column("Network", style="cyan")
    table.add_column("Status")
    table.add_row(
        "Bitcoin Mainnet",
        "BIP-39/BIP-84 offline; read-only Esplora balance lookup (explicit opt-in)",
    )
    table.add_row("Ethereum / EVM", "Planned — not implemented")
    table.add_row("Monero", "Planned — not implemented")
    console.print(table)


@app.command()
def privacy() -> None:
    """Show privacy defaults and network caveats."""
    table = Table(title="Privacy defaults", show_header=True)
    table.add_column("Setting", style="cyan")
    table.add_column("Default")
    settings = AppConfig()
    table.add_row("Telemetry", "Enabled" if settings.telemetry_enabled else "Disabled")
    table.add_row(
        "Network requests", "Enabled" if settings.network_requests_enabled else "Disabled"
    )
    table.add_row("Tor", "Disabled")
    console.print(table)
    console.print(
        "[yellow]Note:[/] Vaultsh does not guarantee anonymity. Wallet creation/recovery are "
        "local/offline. The optional Bitcoin balance command contacts only the endpoint "
        "explicitly supplied by the user, and only after both configuration and command-line "
        "opt-in. The endpoint can associate an address with connection metadata. Tor transport "
        "is not implemented; this command refuses to "
        "connect if tor_enabled is true rather than implying traffic is protected by Tor."
    )


@app.command()
def config() -> None:
    """Print default non-secret application configuration."""
    _print_config(AppConfig(), title="Default configuration")
    console.print("[dim]No secrets are read or displayed by this command.[/]")


def _print_config(settings: AppConfig, *, title: str) -> None:
    table = Table(title=title, show_header=True)
    table.add_column("Setting", style="cyan")
    table.add_column("Value")
    table.add_row("app_name", settings.app_name)
    table.add_row("telemetry_enabled", str(settings.telemetry_enabled).lower())
    table.add_row("network_requests_enabled", str(settings.network_requests_enabled).lower())
    table.add_row("tor_enabled", str(settings.tor_enabled).lower())
    table.add_row("request_timeout_seconds", str(settings.request_timeout_seconds))
    console.print(table)


@app.command("config-init")
def config_init(
    path: Path = typer.Argument(..., help="Path of the TOML file to create."),
    force: bool = typer.Option(False, "--force", help="Replace an existing config file."),
) -> None:
    """Create a non-secret TOML configuration template."""
    if path.exists() and not force:
        console.print(f"[red]Refusing to overwrite existing file:[/] {path}")
        raise typer.Exit(code=1)
    sample = (
        "[app]\n"
        'app_name = "vaultsh"\n'
        "telemetry_enabled = false\n"
        "network_requests_enabled = false\n"
        "tor_enabled = false\n"
        "request_timeout_seconds = 15.0\n"
    )
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(sample, encoding="utf-8")
    except OSError as exc:
        console.print(f"[red]Could not write configuration:[/] {exc}")
        raise typer.Exit(code=1) from exc
    console.print(f"[green]Created config template:[/] {path}")
    console.print(
        "[dim]The file contains preferences only. Never store passwords "
        "or recovery phrases here.[/]"
    )


@app.command("config-check")
def config_check(
    path: Path = typer.Argument(..., help="TOML configuration file to validate.")
) -> None:
    """Validate a TOML configuration without printing secret material."""
    try:
        settings = load_config(path)
    except (ConfigError, OSError) as exc:
        console.print(f"[red]Invalid configuration:[/] {exc}")
        raise typer.Exit(code=1) from exc
    console.print(f"[green]Configuration is valid:[/] {path}")
    _print_config(settings, title="Loaded non-secret configuration")


@vault_app.command("init")
def vault_init(
    path: Path = typer.Argument(..., help="File path for the new encrypted vault."),
    label: str = typer.Option("My Vault", "--label", help="Human-readable vault label."),
) -> None:
    """Create a new encrypted vault metadata container."""
    if path.exists():
        console.print(f"[red]Vault already exists; refusing to overwrite:[/] {path}")
        raise typer.Exit(code=1)
    password = typer.prompt("Vault password", hide_input=True)
    confirmation = typer.prompt("Repeat vault password", hide_input=True)
    if password != confirmation:
        console.print("[red]Passwords do not match. No vault was created.[/]")
        raise typer.Exit(code=1)
    if len(password) < MIN_VAULT_PASSWORD_LENGTH:
        console.print(
            f"[red]Password must contain at least {MIN_VAULT_PASSWORD_LENGTH} characters. "
            "No vault was created.[/]"
        )
        raise typer.Exit(code=1)
    try:
        document = create_vault_document(path, password, label=label)
    except (OSError, ValueError) as exc:
        console.print(f"[red]Could not create vault:[/] {exc}")
        raise typer.Exit(code=1) from exc
    console.print(Panel.fit(
        f"[green]Encrypted metadata container created.[/]\n\n"
        f"Label: {escape(document.label)}\nID: {document.vault_id}\nFile: {escape(str(path))}\n"
        "Wallets: 0",
        title="Vault created",
        border_style="green",
    ))
    console.print("[yellow]This does not create a blockchain wallet or recovery phrase.[/]")


@vault_app.command("check")
def vault_check(path: Path = typer.Argument(..., help="Encrypted vault file to validate.")) -> None:
    """Decrypt and validate vault metadata using a hidden password prompt."""
    password = typer.prompt("Vault password", hide_input=True)
    try:
        document = read_vault_document(path, password)
    except (OSError, ValueError) as exc:
        console.print(f"[red]Vault check failed:[/] {exc}")
        raise typer.Exit(code=1) from exc
    table = Table(title="Vault metadata", show_header=True)
    table.add_column("Field", style="cyan")
    table.add_column("Value")
    table.add_row("Label", escape(document.label))
    table.add_row("Vault ID", document.vault_id)
    table.add_row("Created (ISO 8601)", document.created_at)
    table.add_row("Schema version", str(document.schema_version))
    table.add_row("Wallet records", str(document.wallet_count))
    console.print(table)
    console.print("[green]Password accepted and metadata schema validated.[/]")


@vault_app.command("backup")
def vault_backup(
    source: Path = typer.Argument(..., help="Encrypted vault file."),
    destination: Path = typer.Argument(..., help="New backup path."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Replace existing backup."),
) -> None:
    """Create a byte-for-byte backup of an encrypted vault."""
    try:
        result = create_backup(source, destination, overwrite=overwrite)
    except (OSError, ValueError) as exc:
        console.print(f"[red]Backup failed:[/] {exc}")
        raise typer.Exit(code=1) from exc
    console.print(f"[green]Encrypted backup created:[/] {result}")
    console.print("[yellow]Keep backups private and protect the vault password separately.[/]")


@vault_app.command("restore")
def vault_restore(
    source: Path = typer.Argument(..., help="Encrypted backup file."),
    destination: Path = typer.Argument(..., help="Destination vault path."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Replace an existing destination."),
) -> None:
    """Restore an encrypted backup without decrypting it."""
    try:
        result = restore_backup(source, destination, overwrite=overwrite)
    except (OSError, ValueError) as exc:
        console.print(f"[red]Restore failed:[/] {exc}")
        raise typer.Exit(code=1) from exc
    console.print(f"[green]Encrypted vault restored to:[/] {result}")
    console.print("[dim]Use `vaultsh vault check` to verify it with the vault password.[/]")


@wallet_app.command("create")
def wallet_create(
    vault: Path = typer.Option(..., "--vault", "-v", help="Existing encrypted vault file."),
    label: str = typer.Option("Bitcoin wallet", "--label", help="Wallet label."),
) -> None:
    """Create an offline Bitcoin Mainnet wallet inside an encrypted vault."""
    if not vault.is_file():
        console.print(f"[red]Vault file does not exist:[/] {vault}")
        raise typer.Exit(code=1)
    password = typer.prompt("Vault password", hide_input=True)
    try:
        mnemonic = generate_mnemonic()
        summary = add_bitcoin_wallet(vault, password, label=label, mnemonic=mnemonic)
    except (OSError, ValueError) as exc:
        console.print(f"[red]Wallet creation failed:[/] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(Panel.fit(
        f"[bold]Label:[/] {escape(summary.label)}\n"
        f"[bold]Network:[/] {summary.network}\n"
        f"[bold]Receive address:[/] [cyan]{summary.address}[/]\n"
        f"[bold]Derivation path:[/] {summary.derivation_path}\n"
        f"[bold]Wallet ID:[/] {summary.wallet_id}",
        title="Bitcoin wallet created",
        border_style="green",
    ))
    console.print(Panel(
        f"[bold white]{mnemonic}[/]",
        title="RECOVERY PHRASE — WRITE IT DOWN OFFLINE",
        subtitle="Anyone with this phrase can control the wallet",
        border_style="red",
    ))
    console.print(
        "[yellow]Store the phrase offline and never share it. The phrase is also stored "
        "inside the encrypted vault. Anyone who gets both the file and its password may "
        "recover the wallet. Keep tested backups. No funds should be sent to this pre-alpha "
        "wallet software.[/]"
    )


@wallet_app.command("recover")
def wallet_recover(
    vault: Path = typer.Option(..., "--vault", "-v", help="Existing encrypted vault file."),
    label: str = typer.Option("Recovered Bitcoin wallet", "--label", help="Wallet label."),
) -> None:
    """Import an English BIP-39 phrase into an encrypted vault and derive its address."""
    if not vault.is_file():
        console.print(f"[red]Vault file does not exist:[/] {vault}")
        raise typer.Exit(code=1)
    mnemonic = typer.prompt("Recovery phrase (English BIP-39; input hidden)", hide_input=True)
    password = typer.prompt("Vault password", hide_input=True)
    try:
        summary = add_bitcoin_wallet(vault, password, label=label, mnemonic=mnemonic)
    except (OSError, ValueError) as exc:
        console.print(f"[red]Wallet recovery failed:[/] {exc}")
        raise typer.Exit(code=1) from exc
    console.print(Panel.fit(
        f"[bold]Label:[/] {escape(summary.label)}\n"
        f"[bold]Network:[/] {summary.network}\n"
        f"[bold]Receive address:[/] [cyan]{summary.address}[/]\n"
        f"[bold]Derivation path:[/] {summary.derivation_path}\n"
        f"[bold]Wallet ID:[/] {summary.wallet_id}",
        title="Bitcoin wallet recovered",
        border_style="green",
    ))
    console.print("[dim]The recovery phrase was stored only inside the encrypted vault.[/]")


@wallet_app.command("list")
def wallet_list(
    vault: Path = typer.Option(..., "--vault", "-v", help="Encrypted vault file."),
) -> None:
    """List safe public metadata for wallets stored in an encrypted vault."""
    password = typer.prompt("Vault password", hide_input=True)
    try:
        wallets = list_wallets(vault, password)
    except (OSError, ValueError) as exc:
        console.print(f"[red]Could not list wallets:[/] {exc}")
        raise typer.Exit(code=1) from exc
    if not wallets:
        console.print("[dim]This vault does not contain any wallet records.[/]")
        return
    table = Table(title="Wallets in vault", show_header=True)
    table.add_column("ID", style="dim")
    table.add_column("Label", style="cyan")
    table.add_column("Network")
    table.add_column("Receive address")
    table.add_column("Derivation path")
    for wallet in wallets:
        table.add_row(
            wallet.wallet_id,
            escape(wallet.label),
            wallet.network,
            wallet.address,
            wallet.derivation_path,
        )
    console.print(table)
    console.print("[dim]Recovery phrases are not shown by this command.[/]")


@wallet_app.command("recovery-phrase")
def wallet_recovery_phrase(
    wallet_id: str = typer.Argument(..., help="Wallet ID shown by `wallet list`."),
    vault: Path = typer.Option(..., "--vault", "-v", help="Encrypted vault file."),
) -> None:
    """Explicitly reveal a wallet's recovery phrase after user confirmation."""
    if not typer.confirm(
        "This displays a secret phrase on screen. Continue only in a private place.",
        default=False,
    ):
        console.print("[dim]Cancelled; no recovery phrase was displayed.[/]")
        raise typer.Exit(code=0)
    password = typer.prompt("Vault password", hide_input=True)
    try:
        mnemonic = get_recovery_phrase(vault, password, wallet_id)
    except (OSError, ValueError) as exc:
        console.print(f"[red]Could not reveal recovery phrase:[/] {exc}")
        raise typer.Exit(code=1) from exc
    console.print(Panel(
        f"[bold white]{mnemonic}[/]",
        title="RECOVERY PHRASE — SECRET",
        subtitle="Never share this phrase or store it in screenshots/cloud notes",
        border_style="red",
    ))


@bitcoin_app.command("balance")
def bitcoin_balance(
    address: str = typer.Argument(..., help="Bitcoin Mainnet address to query."),
    endpoint: str = typer.Option(
        ...,
        "--endpoint",
        help="Explicit Esplora API base URL; no public provider is selected by default.",
    ),
    config_path: Path = typer.Option(
        ...,
        "--config",
        help=r"TOML config with \[app].network_requests_enabled = true.",
    ),
    allow_network: bool = typer.Option(
        False,
        "--allow-network",
        help="Explicitly authorize this address lookup and its network metadata exposure.",
    ),
) -> None:
    """Fetch read-only address statistics from a user-selected Esplora endpoint."""
    try:
        settings = load_config(config_path)
        require_network_access(
            explicitly_requested=allow_network,
            configured=settings.network_requests_enabled,
        )
        if settings.tor_enabled:
            raise NetworkAccessDenied(
                "Tor is enabled in config, but Tor transport is not implemented. "
                "No direct connection was made. Disable tor_enabled or wait for a "
                "supported transport."
            )
        client = BitcoinEsploraClient(
            endpoint,
            timeout_seconds=settings.request_timeout_seconds,
        )
    except (ConfigError, OSError, NetworkAccessDenied, NetworkError, ValueError) as exc:
        console.print(f"[red]Bitcoin balance lookup failed:[/] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(
        "[yellow]Privacy notice:[/] If the address is valid, this query sends it and connection "
        "metadata to the endpoint you specified. Vaultsh does not route this request through Tor."
    )
    try:
        balance = client.get_address_balance(address)
    except NetworkError as exc:
        console.print(f"[red]Bitcoin balance lookup failed:[/] {exc}")
        raise typer.Exit(code=1) from exc
    table = Table(title="Bitcoin Mainnet address balance", show_header=True)
    table.add_column("Measure", style="cyan")
    table.add_column("BTC", justify="right")
    table.add_column("Satoshis", justify="right")
    table.add_row("Confirmed", format_btc(balance.confirmed_sats), str(balance.confirmed_sats))
    table.add_row(
        "Net unconfirmed change",
        format_btc(balance.unconfirmed_sats),
        str(balance.unconfirmed_sats),
    )
    table.add_row(
        "Estimated total",
        format_btc(balance.estimated_total_sats),
        str(balance.estimated_total_sats),
    )
    console.print(table)
    console.print(f"Address: {escape(balance.address)}")
    console.print(f"Source: {escape(endpoint)}")
    console.print(
        "[dim]Read-only third-party/node data; it is not a transaction capability or a "
        "proof of ownership.[/]"
    )


@app.command()
def version() -> None:
    """Print the installed Vaultsh version."""
    console.print(f"Vaultsh {__version__}")


if __name__ == "__main__":
    app()
