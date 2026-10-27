"""Vaultsh command-line interface; no blockchain wallet operations yet."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from vaultsh import __version__
from vaultsh.config import AppConfig

app = typer.Typer(
    name="vaultsh",
    help="Privacy-focused, self-custodial multi-chain wallet (pre-alpha).",
    no_args_is_help=False,
    add_completion=False,
)
console = Console()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Show a landing screen when no command is supplied."""
    if ctx.invoked_subcommand is not None:
        return

    table = Table(show_header=False, box=None, pad_edge=False)
    table.add_row("[bold cyan]about[/]     Project status and limitations")
    table.add_row("[bold cyan]networks[/]  Planned blockchain adapters")
    table.add_row("[bold cyan]privacy[/]   Privacy defaults")
    table.add_row("[bold cyan]config[/]    Default non-secret configuration")
    console.print(
        Panel(
            table,
            title=f"[bold cyan]VAULTSH[/] [dim]v{__version__}[/]",
            subtitle="[dim]Private · Self-custodial · Terminal-native[/]",
            border_style="cyan",
        )
    )
    console.print(
        "[yellow]PRE-ALPHA:[/] Do not use this build for real funds. "
        "Wallet generation and transaction operations are not implemented."
    )
    console.print("Run [cyan]vaultsh --help[/] to see commands.")


@app.command()
def about() -> None:
    """Display project scope and current implementation status."""
    message = "\n\n".join(
        [
            "Vaultsh is a Python-first, privacy-focused multi-chain wallet project.",
            "Implemented foundation: CLI, validated non-secret configuration, privacy-policy "
            "helpers, and a small authenticated-encryption/file-storage primitive.",
            "Not implemented: wallet/seed generation or import, chain-specific private-key "
            "derivation, balance retrieval, transaction signing, and broadcasting.",
            "This pre-alpha build is not suitable for real funds.",
        ]
    )
    console.print(Panel(message, title="About Vaultsh", border_style="cyan"))


@app.command()
def networks() -> None:
    """Show currently planned network integrations and their status."""
    table = Table(title="Network adapter roadmap")
    table.add_column("Network", style="cyan")
    table.add_column("Status")
    table.add_row("Bitcoin", "Planned — not implemented")
    table.add_row("Ethereum / EVM", "Planned — not implemented")
    table.add_row("Monero", "Planned — not implemented")
    console.print(table)


@app.command()
def privacy() -> None:
    """Show privacy defaults and network caveats."""
    table = Table(title="Privacy defaults", show_header=True)
    table.add_column("Setting", style="cyan")
    table.add_column("Default")
    config = AppConfig()
    table.add_row("Telemetry", "Enabled" if config.telemetry_enabled else "Disabled")
    table.add_row("Network requests", "Enabled" if config.network_requests_enabled else "Disabled")
    table.add_row("Tor", "Disabled")
    console.print(table)
    console.print(
        "[yellow]Note:[/] Vaultsh does not guarantee anonymity. Public-chain activity can be "
        "traceable; Tor support is configuration-only and not implemented as a transport."
    )


@app.command()
def config() -> None:
    """Print default non-secret application configuration."""
    settings = AppConfig()
    table = Table(title="Default configuration", show_header=True)
    table.add_column("Setting", style="cyan")
    table.add_column("Value")
    table.add_row("app_name", settings.app_name)
    table.add_row("telemetry_enabled", str(settings.telemetry_enabled).lower())
    table.add_row("network_requests_enabled", str(settings.network_requests_enabled).lower())
    table.add_row("tor_enabled", str(settings.tor_enabled).lower())
    table.add_row("request_timeout_seconds", str(settings.request_timeout_seconds))
    console.print(table)
    console.print("[dim]No secrets are read or displayed by this command.[/]")


@app.command()
def version() -> None:
    """Print the installed Vaultsh version."""
    console.print(f"Vaultsh {__version__}")


if __name__ == "__main__":
    app()
