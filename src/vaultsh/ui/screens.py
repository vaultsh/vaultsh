"""Readable first-run dashboard screens built with Rich primitives."""

from __future__ import annotations

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from vaultsh.ui.i18n import tr


def render_dashboard(console: Console, version: str) -> None:
    """Render a grouped start screen with quick steps, feature boundaries, and help hints."""
    heading = Text.assemble(
        ("VAULTSH", "bold cyan"),
        (f"  v{version}\n", "dim"),
        (tr("home.subtitle"), "white"),
    )
    console.print(Panel(heading, border_style="cyan", padding=(1, 2)))

    commands = Table(
        title=tr("home.commands_title"),
        show_header=True,
        header_style="bold cyan",
        expand=True,
        pad_edge=False,
    )
    commands.add_column(tr("home.command"), style="cyan", no_wrap=True, ratio=1)
    commands.add_column(tr("home.purpose"), ratio=3)
    commands.add_row("[bold]vault init[/]", tr("home.vault_init"))
    commands.add_row("[bold]vault check[/]", tr("home.vault_check"))
    commands.add_row("[bold]vault backup[/]", tr("home.vault_backup"))
    commands.add_row("[bold]vault restore[/]", tr("home.vault_restore"))
    commands.add_section()
    commands.add_row("[bold]wallet create[/]", tr("home.wallet_create"))
    commands.add_row("[bold]wallet recover[/]", tr("home.wallet_recover"))
    commands.add_row("[bold]wallet list[/]", tr("home.wallet_list"))
    commands.add_section()
    commands.add_row("[bold]bitcoin balance[/]", tr("home.btc_balance"))
    commands.add_row("[bold]bitcoin history[/]", tr("home.btc_history"))
    commands.add_row("[bold]evm balance[/]", tr("home.evm_balance"))
    commands.add_section()
    commands.add_row("[bold]about[/]", tr("home.about"))
    commands.add_row("[bold]networks[/]", tr("home.networks"))
    commands.add_row("[bold]privacy[/]", tr("home.privacy"))
    commands.add_row("[bold]config[/]", tr("home.config"))
    console.print(commands)

    quick_start = Panel(
        Text(tr("home.quickstart_body")),
        title=tr("home.quickstart_title"),
        border_style="green",
        padding=(1, 2),
    )
    warning = Panel(
        Group(
            Text(tr("home.status_body"), style="bold yellow"),
            Text(tr("home.network_notice")),
        ),
        title=tr("home.status_title"),
        border_style="yellow",
        padding=(1, 2),
    )
    console.print(Group(quick_start, warning))
    console.print(Text(tr("home.help_hint"), style="dim"))
