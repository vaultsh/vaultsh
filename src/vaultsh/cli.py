"""Vaultsh command-line interface.

The beta CLI provides encrypted wallet records, address QR codes, read-only chain queries,
and explicitly confirmed transaction signing/broadcast for BTC, ETH, SOL, and local Monero RPC.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit

import typer
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table

from vaultsh import __version__
from vaultsh.config import AppConfig, ConfigError, load_config
from vaultsh.networks.base import NetworkError
from vaultsh.networks.bitcoin.client import (
    BitcoinAddressTransaction,
    BitcoinEsploraClient,
    format_btc,
)
from vaultsh.networks.bitcoin.wallet import generate_mnemonic
from vaultsh.networks.bitcoin.transfer import BitcoinPaymentClient, prepare_bitcoin_transfer
from vaultsh.networks.ethereum.transfer import (
    broadcast_evm_transfer,
    prepare_evm_transfer,
)
from vaultsh.networks.solana.client import SolanaRpcClient, format_sol
from vaultsh.networks.monero.rpc import MoneroWalletRpcClient, format_xmr
from vaultsh.networks.ethereum.client import (
    EVM_NETWORKS,
    EvmJsonRpcClient,
    format_native_asset,
    get_evm_network_profile,
)
from vaultsh.privacy.network_policy import NetworkAccessDenied, require_network_access
from vaultsh.storage.backup import create_backup, restore_backup
from vaultsh.storage.vault_document import (
    MIN_VAULT_PASSWORD_LENGTH,
    create_vault_document,
    read_vault_document,
)
from vaultsh.storage.wallet_store import (
    add_bitcoin_wallet, add_multichain_wallet, get_recovery_phrase, get_wallet_record, list_wallets,
)
from vaultsh.ui.qr import QrError, render_address_qr, save_address_qr
from vaultsh.ui.i18n import get_language, set_language, tr
from vaultsh.ui.screens import render_dashboard

app = typer.Typer(
    name="vaultsh",
    help="Vaultsh 1.0 Beta: self-custody wallet; test carefully, not independently audited.",
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
    help="Create, recover, list, and display public-address QR codes for supported wallets.",
    no_args_is_help=True,
)
app.add_typer(wallet_app, name="wallet")
bitcoin_app = typer.Typer(
    name="bitcoin",
    help="Bitcoin Mainnet balance/history and locally signed BTC sends via an explicit Esplora endpoint.",
    no_args_is_help=True,
)
app.add_typer(bitcoin_app, name="bitcoin")
ethereum_app = typer.Typer(
    name="ethereum",
    help="Ethereum Mainnet balance and locally signed native ETH transfers via explicit JSON-RPC.",
    no_args_is_help=True,
)
app.add_typer(ethereum_app, name="ethereum")
evm_app = typer.Typer(
    name="evm",
    help="Read-only native-asset queries for explicitly supported EVM mainnets (only ETH Mainnet transfers are enabled).",
    no_args_is_help=True,
)
app.add_typer(evm_app, name="evm")
console = Console()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    lang: str = typer.Option(
        "en",
        "--lang",
        "-L",
        help="Interface language: en (English), pl (Polski), ru (Русский). Place before the command.",
        show_default=True,
        case_sensitive=False,
    ),
) -> None:
    """Show a readable command dashboard when no subcommand is supplied."""
    try:
        set_language(lang)
    except ValueError as exc:
        console.print(f"[red]Invalid interface language:[/] {escape(str(exc))}")
        raise typer.Exit(code=2) from exc
    if ctx.invoked_subcommand is not None:
        return
    # Interactive terminals get the full-screen Textual app by default. In CI,
    # pipes, and captured output, keep the stable Rich dashboard so commands are
    # scriptable and the program never unexpectedly takes over a non-interactive TTY.
    if console.is_terminal:
        _launch_textual_ui(get_language())
    else:
        render_dashboard(console, __version__)


def _launch_textual_ui(language: str, config_path: Path = Path("./vaultsh.toml")) -> None:
    try:
        from vaultsh.ui.tui import run_tui
    except ImportError as exc:
        console.print(
            "[red]The Textual interface is unavailable.[/] Install project dependencies with "
            "[bold]python -m pip install -e .[/]."
        )
        raise typer.Exit(code=2) from exc
    run_tui(language=language, config_path=config_path)


@app.command("ui")
def ui_command(
    config_path: Path = typer.Option(
        Path("./vaultsh.toml"), "--config", help="Non-secret TOML settings file to load."
    )
) -> None:
    """Launch the full-screen Textual user interface."""
    _launch_textual_ui(get_language(), config_path)


@app.command("tui")
def tui_command(
    config_path: Path = typer.Option(
        Path("./vaultsh.toml"), "--config", help="Non-secret TOML settings file to load."
    )
) -> None:
    """Alias for the full-screen Textual interface."""
    _launch_textual_ui(get_language(), config_path)


@app.command()
def about() -> None:
    """Display project scope and current implementation status."""
    message = "\n\n".join(
        [
            tr("about.summary"),
            tr("about.implemented"),
            tr("about.missing"),
            tr("about.warning"),
        ]
    )
    console.print(Panel(message, title=tr("about.title"), border_style="cyan", padding=(1, 2)))


@app.command()
def networks() -> None:
    """Show the chain profiles available in this beta and their feature boundaries."""
    table = Table(title=tr("networks.title"), show_header=True, expand=True)
    table.add_column(tr("networks.network"), style="cyan")
    table.add_column(tr("networks.status"))
    table.add_row("Bitcoin Mainnet", tr("networks.bitcoin"))
    for profile in EVM_NETWORKS.values():
        table.add_row(
            profile.name,
            tr("networks.evm_status").format(
                asset=profile.asset_symbol, chain_id=profile.chain_id
            ),
        )
    table.add_row("Solana Mainnet", tr("networks.solana"))
    table.add_row("Monero Mainnet", tr("networks.monero"))
    console.print(table)


@app.command()
def privacy() -> None:
    """Show privacy defaults and network caveats."""
    table = Table(title=tr("privacy.title"), show_header=True, expand=True)
    table.add_column(tr("privacy.setting"), style="cyan")
    table.add_column(tr("privacy.default"))
    settings = AppConfig()
    disabled = tr("privacy.disabled")
    table.add_row(tr("privacy.telemetry"), "Enabled" if settings.telemetry_enabled else disabled)
    table.add_row(
        tr("privacy.network"), "Enabled" if settings.network_requests_enabled else disabled
    )
    table.add_row(tr("privacy.tor"), disabled)
    console.print(table)
    console.print(Panel(tr("privacy.note"), border_style="yellow", padding=(1, 2)))


@app.command()
def config() -> None:
    """Print default non-secret application configuration."""
    _print_config(AppConfig(), title=tr("config.title"))
    console.print(f"[dim]{tr('config.no_secrets')}[/]")


def _print_config(settings: AppConfig, *, title: str) -> None:
    table = Table(title=title, show_header=True, expand=True)
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
    label: str = typer.Option("Wallet", "--label", help="Wallet label."),
    network: str = typer.Option("bitcoin", "--network", help="bitcoin, ethereum, or solana."),
) -> None:
    """Create a BIP-39 wallet and store the recovery phrase in the encrypted vault."""
    if not vault.is_file():
        console.print(f"[red]Vault file does not exist:[/] {vault}")
        raise typer.Exit(code=1)
    network_map = {
        "bitcoin": "bitcoin-mainnet", "bitcoin-mainnet": "bitcoin-mainnet",
        "ethereum": "ethereum-mainnet", "ethereum-mainnet": "ethereum-mainnet",
        "solana": "solana-mainnet", "solana-mainnet": "solana-mainnet",
    }
    canonical_network = network_map.get(network.strip().lower())
    if canonical_network is None:
        console.print("[red]Supported seed-based wallets: bitcoin, ethereum, solana.[/]")
        console.print("[yellow]Monero is managed separately by monero-wallet-rpc.[/]")
        raise typer.Exit(code=2)
    password = typer.prompt("Vault password", hide_input=True)
    try:
        mnemonic = generate_mnemonic()
        if canonical_network == "bitcoin-mainnet":
            summary = add_bitcoin_wallet(vault, password, label=label, mnemonic=mnemonic)
        else:
            summary = add_multichain_wallet(
                vault, password, label=label, network=canonical_network, mnemonic=mnemonic
            )
    except (OSError, ValueError) as exc:
        console.print(f"[red]Wallet creation failed:[/] {exc}")
        raise typer.Exit(code=1) from exc
    console.print(Panel.fit(
        f"[bold]Label:[/] {escape(summary.label)}\n"
        f"[bold]Network:[/] {summary.network}\n"
        f"[bold]Receive address:[/] [cyan]{summary.address}[/]\n"
        f"[bold]Derivation path:[/] {summary.derivation_path}\n"
        f"[bold]Wallet ID:[/] {summary.wallet_id}",
        title="Wallet created", border_style="green",
    ))
    console.print(Panel(
        f"[bold white]{mnemonic}[/]",
        title="RECOVERY PHRASE — WRITE IT DOWN OFFLINE",
        subtitle="Anyone with this phrase can control this wallet",
        border_style="red",
    ))
    console.print(
        "[yellow]Beta software: use testnet/devnet first where supported. Never share this phrase. "
        "Vaultsh stores it inside the encrypted vault; keep an offline backup.[/]"
    )


@wallet_app.command("recover")
def wallet_recover(
    vault: Path = typer.Option(..., "--vault", "-v", help="Existing encrypted vault file."),
    label: str = typer.Option("Recovered wallet", "--label", help="Wallet label."),
    network: str = typer.Option("bitcoin", "--network", help="bitcoin, ethereum, or solana."),
) -> None:
    """Import a BIP-39 phrase into an encrypted vault for a supported chain."""
    if not vault.is_file():
        console.print(f"[red]Vault file does not exist:[/] {vault}")
        raise typer.Exit(code=1)
    network_map = {
        "bitcoin": "bitcoin-mainnet", "bitcoin-mainnet": "bitcoin-mainnet",
        "ethereum": "ethereum-mainnet", "ethereum-mainnet": "ethereum-mainnet",
        "solana": "solana-mainnet", "solana-mainnet": "solana-mainnet",
    }
    canonical_network = network_map.get(network.strip().lower())
    if canonical_network is None:
        console.print("[red]Supported seed-based wallets: bitcoin, ethereum, solana.[/]")
        raise typer.Exit(code=2)
    mnemonic = typer.prompt("Recovery phrase (English BIP-39; input hidden)", hide_input=True)
    password = typer.prompt("Vault password", hide_input=True)
    try:
        if canonical_network == "bitcoin-mainnet":
            summary = add_bitcoin_wallet(vault, password, label=label, mnemonic=mnemonic)
        else:
            summary = add_multichain_wallet(
                vault, password, label=label, network=canonical_network, mnemonic=mnemonic
            )
    except (OSError, ValueError) as exc:
        console.print(f"[red]Wallet recovery failed:[/] {exc}")
        raise typer.Exit(code=1) from exc
    console.print(Panel.fit(
        f"[bold]Label:[/] {escape(summary.label)}\n"
        f"[bold]Network:[/] {summary.network}\n"
        f"[bold]Receive address:[/] [cyan]{summary.address}[/]\n"
        f"[bold]Derivation path:[/] {summary.derivation_path}\n"
        f"[bold]Wallet ID:[/] {summary.wallet_id}",
        title="Wallet recovered", border_style="green",
    ))


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
    source_host = urlsplit(client.endpoint).hostname or "configured endpoint"
    console.print(f"Source host: {escape(source_host)}")
    console.print(
        "[dim]Read-only third-party/node data; it is not a transaction capability or a "
        "proof of ownership.[/]"
    )


@bitcoin_app.command("history")
def bitcoin_history(
    address: str = typer.Argument(..., help="Bitcoin Mainnet address to query."),
    endpoint: str = typer.Option(..., "--endpoint", help="Explicit Esplora API base URL."),
    config_path: Path = typer.Option(..., "--config", help="TOML config enabling network requests."),
    allow_network: bool = typer.Option(
        False,
        "--allow-network",
        help="Explicitly authorize address history lookup and metadata exposure.",
    ),
    limit: int = typer.Option(10, "--limit", min=1, max=25, help="Maximum first-page rows (1-25)."),
) -> None:
    """Fetch a limited, newest-first transaction history for one Bitcoin address."""
    try:
        settings = load_config(config_path)
        require_network_access(
            explicitly_requested=allow_network,
            configured=settings.network_requests_enabled,
        )
        if settings.tor_enabled:
            raise NetworkAccessDenied(
                "Tor is enabled in config, but Tor transport is not implemented. "
                "No direct connection was made."
            )
        client = BitcoinEsploraClient(endpoint, timeout_seconds=settings.request_timeout_seconds)
    except (ConfigError, OSError, NetworkAccessDenied, NetworkError, ValueError) as exc:
        console.print(f"[red]Bitcoin history lookup failed:[/] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(
        "[yellow]Privacy notice:[/] This sends the address to your selected endpoint. "
        "Tor routing is not implemented."
    )
    try:
        transactions = client.get_address_transactions(address, limit=limit)
    except NetworkError as exc:
        console.print(f"[red]Bitcoin history lookup failed:[/] {exc}")
        raise typer.Exit(code=1) from exc
    if not transactions:
        console.print("[dim]No transactions were returned for this address.[/]")
        return
    table = Table(title="Bitcoin Mainnet — address transaction history", show_header=True)
    table.add_column("Transaction ID", style="cyan")
    table.add_column("Status")
    table.add_column("Block height")
    table.add_column("Block time (UTC)")
    table.add_column("Fee (BTC)", justify="right")
    for transaction in transactions:
        table.add_row(
            transaction.txid,
            "Confirmed" if transaction.confirmed else "Unconfirmed",
            str(transaction.block_height) if transaction.block_height is not None else "—",
            _format_block_time(transaction),
            format_btc(transaction.fee_sats) if transaction.fee_sats is not None else "—",
        )
    console.print(table)
    console.print(
        "[dim]This is the first page for one address, not full wallet history. "
        "Results are provider-supplied and not independently verified.[/]"
    )


def _format_block_time(transaction: BitcoinAddressTransaction) -> str:
    if transaction.block_time is None:
        return "—"
    try:
        return datetime.fromtimestamp(transaction.block_time, tz=UTC).isoformat(timespec="seconds")
    except (OverflowError, OSError, ValueError):
        return "Invalid timestamp"


@ethereum_app.command("balance")
def ethereum_balance(
    address: str = typer.Argument(..., help="Ethereum Mainnet 0x-prefixed account address."),
    endpoint: str = typer.Option(..., "--endpoint", help="Explicit Ethereum Mainnet JSON-RPC endpoint."),
    config_path: Path = typer.Option(..., "--config", help="TOML config enabling network requests."),
    allow_network: bool = typer.Option(
        False,
        "--allow-network",
        help="Explicitly authorize this address lookup and its metadata exposure.",
    ),
) -> None:
    """Fetch native ETH balance from Ethereum Mainnet."""
    _run_evm_balance(
        address=address,
        endpoint=endpoint,
        config_path=config_path,
        allow_network=allow_network,
        chain_key="ethereum",
    )


@evm_app.command("balance")
def evm_balance(
    address: str = typer.Argument(..., help="EVM account address (0x plus 40 hexadecimal characters)."),
    chain: str = typer.Option(
        "ethereum",
        "--chain",
        help="Supported mainnet: ethereum, polygon, arbitrum, optimism, or base.",
        case_sensitive=False,
    ),
    endpoint: str = typer.Option(..., "--endpoint", help="Explicit JSON-RPC endpoint for the chosen chain."),
    config_path: Path = typer.Option(..., "--config", help="TOML config enabling network requests."),
    allow_network: bool = typer.Option(
        False,
        "--allow-network",
        help="Explicitly authorize this address lookup and its metadata exposure.",
    ),
) -> None:
    """Fetch a supported EVM network's native asset balance at the latest block."""
    _run_evm_balance(
        address=address,
        endpoint=endpoint,
        config_path=config_path,
        allow_network=allow_network,
        chain_key=chain,
    )


def _run_evm_balance(
    *, address: str, endpoint: str, config_path: Path, allow_network: bool, chain_key: str
) -> None:
    """Shared fail-closed read-only EVM balance path for both CLI command groups."""
    try:
        profile = get_evm_network_profile(chain_key)
        settings = load_config(config_path)
        require_network_access(
            explicitly_requested=allow_network,
            configured=settings.network_requests_enabled,
        )
        if settings.tor_enabled:
            raise NetworkAccessDenied(
                "Tor is enabled in config, but Tor transport is not implemented. "
                "No direct connection was made."
            )
        client = EvmJsonRpcClient(
            endpoint,
            timeout_seconds=settings.request_timeout_seconds,
            expected_chain_id=profile.chain_id,
            network_name=profile.name,
            asset_symbol=profile.asset_symbol,
        )
    except (ConfigError, OSError, NetworkAccessDenied, NetworkError, ValueError) as exc:
        console.print(f"[red]EVM balance lookup failed:[/] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(
        "[yellow]Privacy notice:[/] This sends the address to your selected JSON-RPC endpoint. "
        "It can observe connection metadata; Vaultsh does not route through Tor."
    )
    try:
        balance = client.get_address_balance(address)
    except NetworkError as exc:
        console.print(f"[red]EVM balance lookup failed:[/] {exc}")
        raise typer.Exit(code=1) from exc
    table = Table(title=f"{balance.network_name} address balance", show_header=True)
    table.add_column("Measure", style="cyan")
    table.add_column("Value", justify="right")
    table.add_row(
        f"Native {balance.asset_symbol} balance at latest block",
        format_native_asset(balance.balance_base_units),
    )
    base_unit_name = "wei" if balance.asset_symbol == "ETH" else "base units"
    table.add_row(base_unit_name, str(balance.balance_base_units))
    table.add_row("Chain ID", str(balance.chain_id))
    console.print(table)
    console.print(f"Address: {escape(balance.address)}")
    host = urlsplit(client.endpoint).hostname or "configured endpoint"
    console.print(f"RPC host: {escape(host)}")
    console.print(
        "[dim]This is a provider-supplied read-only result, not a proof of ownership. "
        "Vaultsh does not derive EVM private keys, query ERC-20 token balances, or send transactions.[/]"
    )


@wallet_app.command("qr")
def wallet_qr(
    wallet_id: str = typer.Argument(..., help="Wallet ID from `vaultsh wallet list`."),
    vault: Path = typer.Option(..., "--vault", "-v", help="Encrypted vault file."),
    output: Path | None = typer.Option(None, "--output", help="Optional new PNG output path."),
) -> None:
    """Show the QR for a public address stored in the encrypted vault."""
    password = typer.prompt("Vault password", hide_input=True)
    try:
        records = list_wallets(vault, password)
    except (OSError, ValueError) as exc:
        console.print(f"[red]Could not read vault:[/] {exc}")
        raise typer.Exit(code=1) from exc
    wallet = next((record for record in records if record.wallet_id == wallet_id), None)
    if wallet is None:
        console.print("[red]Wallet ID was not found in this vault.[/]")
        raise typer.Exit(code=1)
    try:
        if output is not None:
            result_path = save_address_qr(wallet.address, output)
            console.print(f"[green]Public address QR saved:[/] {escape(str(result_path))}")
        console.print(Panel(render_address_qr(wallet.address), title=f"{wallet.network} — public address QR", border_style="orange"))
        console.print(f"[bold]Address:[/] {escape(wallet.address)}")
        console.print("[dim]This QR contains only the public receive address, never a recovery phrase or private key.[/]")
    except (QrError, OSError, ValueError) as exc:
        console.print(f"[red]Could not render QR:[/] {escape(str(exc))}")
        raise typer.Exit(code=1) from exc


@app.command("qr")
def qr_address(
    address: str = typer.Argument(..., help="Public blockchain address to encode."),
    output: Path | None = typer.Option(None, "--output", help="Optional new PNG output path."),
) -> None:
    """Render a QR for any public address; no private information is accepted."""
    try:
        if output is not None:
            result_path = save_address_qr(address, output)
            console.print(f"[green]Public address QR saved:[/] {escape(str(result_path))}")
        console.print(Panel(render_address_qr(address), title="Public address QR", border_style="orange"))
        console.print(f"[bold]Address:[/] {escape(address)}")
    except (QrError, OSError, ValueError) as exc:
        console.print(f"[red]QR generation failed:[/] {escape(str(exc))}")
        raise typer.Exit(code=1) from exc


def _load_network_settings(config_path: Path, allow_network: bool) -> AppConfig:
    """Enforce config + per-command consent and refuse unsupported Tor transport."""
    settings = load_config(config_path)
    require_network_access(
        explicitly_requested=allow_network,
        configured=settings.network_requests_enabled,
    )
    if settings.tor_enabled:
        raise NetworkAccessDenied(
            "Tor is enabled in the Vaultsh config, but this release does not implement Tor transport. "
            "No connection was made. Disable tor_enabled or use a separately verified Tor setup."
        )
    return settings


def _confirm_transfer(
    *, symbol: str, amount: str, destination: str, fee: str | None = None
) -> bool:
    """Require a typed, exact confirmation that includes the shown fee estimate."""
    phrase = f"SEND {symbol} {amount} TO {destination}"
    fee_line = ""
    if fee is not None:
        phrase += f" WITH FEE UP TO {fee} {symbol}"
        fee_line = f"\nFee (maximum/estimated): [bold]{escape(fee)} {escape(symbol)}[/]"
    console.print(Panel(
        f"[bold yellow]You are about to broadcast a real blockchain transaction.[/]\n\n"
        f"Asset: [bold]{escape(symbol)}[/]\nAmount: [bold]{escape(amount)}[/]\n"
        f"Destination: [bold]{escape(destination)}[/]{fee_line}\n\n"
        f"Type exactly:\n[bold red]{escape(phrase)}[/]",
        title="FINAL TRANSFER CONFIRMATION", border_style="red", padding=(1, 2),
    ))
    try:
        typed = typer.prompt("Confirmation", default="")
    except (EOFError, typer.Abort):
        return False
    return typed == phrase


@bitcoin_app.command("send")
def bitcoin_send(
    wallet_id: str = typer.Option(..., "--wallet-id", help="Bitcoin wallet ID stored in the vault."),
    vault: Path = typer.Option(..., "--vault", help="Encrypted Vaultsh wallet file."),
    destination: str = typer.Option(..., "--to", help="Bitcoin Mainnet recipient address."),
    amount: str = typer.Option(..., "--amount", help="BTC amount, up to 8 decimal places."),
    endpoint: str = typer.Option(..., "--endpoint", help="Explicit Esplora API base URL."),
    config_path: Path = typer.Option(Path("./vaultsh.toml"), "--config", help="Config allowing network access."),
    allow_network: bool = typer.Option(False, "--allow-network", help="Authorize this operation to access the network."),
    max_fee_sats: int = typer.Option(100_000, "--max-fee-sats", min=1, max=10_000_000, help="Maximum accepted fee in satoshis."),
) -> None:
    """Prepare, locally sign, preview, and explicitly broadcast a Bitcoin Mainnet payment."""
    password = typer.prompt("Vault password", hide_input=True)
    try:
        settings = _load_network_settings(config_path, allow_network)
        record = get_wallet_record(vault, password, wallet_id)
        if record.get("network") != "bitcoin-mainnet":
            raise NetworkError("Selected wallet is not a Bitcoin Mainnet wallet")
        client = BitcoinPaymentClient(endpoint, timeout_seconds=settings.request_timeout_seconds)
        utxos = client.get_confirmed_utxos(record["address"])
        fee_rate = client.get_fee_rate()
        preview = prepare_bitcoin_transfer(
            mnemonic=record["mnemonic"], expected_sender=record["address"], destination=destination,
            amount=amount, utxos=utxos, fee_rate_sat_vb=fee_rate, max_fee_sats=max_fee_sats,
        )
    except (ConfigError, NetworkAccessDenied, NetworkError, OSError, ValueError) as exc:
        console.print(f"[red]Bitcoin transfer preparation failed:[/] {escape(str(exc))}")
        raise typer.Exit(code=1) from exc
    console.print(Panel(
        f"Network: Bitcoin Mainnet\nFrom: {preview.sender}\nTo: {preview.destination}\n"
        f"Amount: {format_btc(preview.amount_sats)} BTC\nEstimated/final fee: {format_btc(preview.fee_sats)} BTC ({preview.fee_sats} sats)\n"
        f"Confirmed inputs: {preview.input_count}\nChange: {format_btc(preview.change_sats)} BTC\n"
        f"Locally signed transaction ID preview: {preview.txid}",
        title="Review Bitcoin transaction", border_style="orange",
    ))
    console.print("[yellow]Privacy: this query sends your address to the selected Esplora endpoint. Tor is not used.[/]")
    console.print(Panel(
        "CRITICAL BETA LIMITATION: Vaultsh only discovers confirmed UTXOs at the first receive address. "
        "Change is sent to BIP-84 path m/84'/0'/0'/1/0, which this release does not scan. "
        "Do not use this send command with real funds. The recovery phrase can recover the change in a compatible wallet.",
        title="Bitcoin send warning", border_style="red",
    ))
    if not _confirm_transfer(symbol="BTC", amount=format_btc(preview.amount_sats), destination=preview.destination, fee=format_btc(preview.fee_sats)):
        console.print("[dim]Cancelled. The transaction was not broadcast.[/]")
        return
    try:
        txid = client.broadcast(preview.raw_transaction_hex)
    except NetworkError as exc:
        console.print(f"[red]Broadcast failed:[/] {escape(str(exc))}")
        raise typer.Exit(code=1) from exc
    console.print(Panel.fit(f"[green]Transaction submitted.[/]\nTXID: {txid}", title="Bitcoin payment", border_style="green"))


@ethereum_app.command("send")
def ethereum_send(
    wallet_id: str = typer.Option(..., "--wallet-id", help="Ethereum Mainnet wallet ID in the vault."),
    vault: Path = typer.Option(..., "--vault", help="Encrypted Vaultsh wallet file."),
    destination: str = typer.Option(..., "--to", help="Ethereum 0x destination address."),
    amount: str = typer.Option(..., "--amount", help="ETH amount, up to 18 decimal places."),
    endpoint: str = typer.Option(..., "--endpoint", help="Explicit Ethereum Mainnet JSON-RPC URL."),
    config_path: Path = typer.Option(Path("./vaultsh.toml"), "--config", help="Config allowing network access."),
    allow_network: bool = typer.Option(False, "--allow-network", help="Authorize this operation to access the network."),
    max_fee_eth: str = typer.Option("0.1", "--max-fee-eth", help="Maximum fee cap in ETH."),
) -> None:
    """Prepare, locally sign, preview, and explicitly broadcast a native ETH payment."""
    password = typer.prompt("Vault password", hide_input=True)
    try:
        settings = _load_network_settings(config_path, allow_network)
        record = get_wallet_record(vault, password, wallet_id)
        if record.get("network") != "ethereum-mainnet":
            raise NetworkError("Selected wallet is not an Ethereum Mainnet wallet")
        profile = get_evm_network_profile("ethereum")
        client = EvmJsonRpcClient(
            endpoint, timeout_seconds=settings.request_timeout_seconds,
            expected_chain_id=profile.chain_id, network_name=profile.name, asset_symbol=profile.asset_symbol,
        )
        preview = prepare_evm_transfer(
            endpoint=endpoint, network="ethereum", mnemonic=record["mnemonic"], expected_sender=record["address"],
            destination=destination, amount=amount, timeout_seconds=settings.request_timeout_seconds,
            max_fee_native=max_fee_eth, client=client,
        )
    except (ConfigError, NetworkAccessDenied, NetworkError, OSError, ValueError) as exc:
        console.print(f"[red]Ethereum transfer preparation failed:[/] {escape(str(exc))}")
        raise typer.Exit(code=1) from exc
    console.print(Panel(
        f"Network: {preview.network_name} (chain ID {preview.chain_id})\nFrom: {preview.sender}\nTo: {preview.destination}\n"
        f"Amount: {format_native_asset(preview.amount_base_units)} ETH\nMaximum fee: {format_native_asset(preview.max_fee_wei)} ETH\nNonce: {preview.nonce}",
        title="Review ETH transaction", border_style="orange",
    ))
    console.print("[yellow]The endpoint sees the queried address and connection metadata. Tor is not used.[/]")
    if not _confirm_transfer(symbol="ETH", amount=format_native_asset(preview.amount_base_units), destination=preview.destination, fee=format_native_asset(preview.max_fee_wei)):
        console.print("[dim]Cancelled. The transaction was not broadcast.[/]")
        return
    try:
        tx_hash = broadcast_evm_transfer(preview, client=client)
    except NetworkError as exc:
        console.print(f"[red]ETH broadcast failed:[/] {escape(str(exc))}")
        raise typer.Exit(code=1) from exc
    console.print(Panel.fit(f"[green]Transaction submitted.[/] TX hash: {tx_hash}", title="Ethereum payment", border_style="green"))


solana_app = typer.Typer(help="Solana Mainnet balance and native SOL transfers.", no_args_is_help=True)
app.add_typer(solana_app, name="solana")


@solana_app.command("balance")
def solana_balance(
    address: str = typer.Argument(..., help="Solana Mainnet public address."),
    endpoint: str = typer.Option(..., "--endpoint", help="Explicit Solana Mainnet JSON-RPC URL."),
    config_path: Path = typer.Option(Path("./vaultsh.toml"), "--config", help="Config allowing network access."),
    allow_network: bool = typer.Option(False, "--allow-network", help="Authorize the network query."),
) -> None:
    """Query native SOL balance from a user-selected Mainnet RPC endpoint."""
    try:
        settings = _load_network_settings(config_path, allow_network)
        client = SolanaRpcClient(endpoint, timeout_seconds=settings.request_timeout_seconds)
        balance = client.get_balance(address)
    except (ConfigError, NetworkAccessDenied, NetworkError, OSError, ValueError) as exc:
        console.print(f"[red]Solana balance query failed:[/] {escape(str(exc))}")
        raise typer.Exit(code=1) from exc
    console.print(f"Address: {escape(address)}\nBalance: {format_sol(balance)} SOL ({balance} lamports)")


@solana_app.command("send")
def solana_send(
    wallet_id: str = typer.Option(..., "--wallet-id", help="Solana Mainnet wallet ID in the vault."),
    vault: Path = typer.Option(..., "--vault", help="Encrypted Vaultsh wallet file."),
    destination: str = typer.Option(..., "--to", help="Solana recipient public key."),
    amount: str = typer.Option(..., "--amount", help="SOL amount, up to 9 decimal places."),
    endpoint: str = typer.Option(..., "--endpoint", help="Explicit Solana Mainnet JSON-RPC URL."),
    config_path: Path = typer.Option(Path("./vaultsh.toml"), "--config", help="Config allowing network access."),
    allow_network: bool = typer.Option(False, "--allow-network", help="Authorize this operation to access the network."),
    max_fee_sol: str = typer.Option("0.01", "--max-fee-sol", help="Maximum fee cap in SOL."),
) -> None:
    """Prepare, locally sign, preview, and explicitly broadcast a native SOL payment."""
    password = typer.prompt("Vault password", hide_input=True)
    try:
        settings = _load_network_settings(config_path, allow_network)
        record = get_wallet_record(vault, password, wallet_id)
        if record.get("network") != "solana-mainnet":
            raise NetworkError("Selected wallet is not a Solana Mainnet wallet")
        client = SolanaRpcClient(endpoint, timeout_seconds=settings.request_timeout_seconds)
        preview = client.prepare_transfer(
            mnemonic=record["mnemonic"], expected_sender=record["address"], destination=destination,
            amount=amount, max_fee_sol=max_fee_sol,
        )
    except (ConfigError, NetworkAccessDenied, NetworkError, OSError, ValueError) as exc:
        console.print(f"[red]Solana transfer preparation failed:[/] {escape(str(exc))}")
        raise typer.Exit(code=1) from exc
    console.print(Panel(
        f"Network: Solana Mainnet Beta\nFrom: {preview.sender}\nTo: {preview.destination}\n"
        f"Amount: {format_sol(preview.lamports)} SOL\nFee: {format_sol(preview.fee_lamports)} SOL ({preview.fee_lamports} lamports)\n"
        f"Blockhash: {preview.blockhash}", title="Review SOL transaction", border_style="orange",
    ))
    if not _confirm_transfer(symbol="SOL", amount=format_sol(preview.lamports), destination=preview.destination, fee=format_sol(preview.fee_lamports)):
        console.print("[dim]Cancelled. The transaction was not broadcast.[/]")
        return
    try:
        signature = client.broadcast_transfer(preview)
    except NetworkError as exc:
        console.print(f"[red]Solana broadcast failed:[/] {escape(str(exc))}")
        raise typer.Exit(code=1) from exc
    console.print(Panel.fit(f"[green]Transaction submitted.[/] Signature: {signature}", title="Solana payment", border_style="green"))


monero_app = typer.Typer(help="Monero via a locally running official monero-wallet-rpc service.", no_args_is_help=True)
app.add_typer(monero_app, name="monero")


def _monero_client(rpc_url: str, timeout: float, username: str | None) -> MoneroWalletRpcClient:
    rpc_password = None
    if username:
        rpc_password = typer.prompt("Monero wallet RPC password", hide_input=True)
    return MoneroWalletRpcClient(rpc_url, timeout_seconds=timeout, username=username, password=rpc_password)


@monero_app.command("create-wallet")
def monero_create_wallet(
    name: str = typer.Argument(..., help="Wallet filename within monero-wallet-rpc's configured wallet directory."),
    rpc_url: str = typer.Option("http://127.0.0.1:18082/json_rpc", "--rpc-url", help="Loopback monero-wallet-rpc URL."),
    config_path: Path = typer.Option(Path("./vaultsh.toml"), "--config", help="Config allowing wallet RPC calls."),
    allow_network: bool = typer.Option(False, "--allow-network", help="Authorize the local wallet RPC call."),
    rpc_username: str | None = typer.Option(None, "--rpc-username", help="Optional monero-wallet-rpc digest-auth user."),
) -> None:
    """Create a Monero wallet using the official locally running monero-wallet-rpc."""
    try:
        settings = _load_network_settings(config_path, allow_network)
        client = _monero_client(rpc_url, settings.request_timeout_seconds, rpc_username)
        wallet_password = typer.prompt("New Monero wallet password", hide_input=True)
        confirmation = typer.prompt("Repeat Monero wallet password", hide_input=True)
        if wallet_password != confirmation:
            raise NetworkError("Wallet passwords do not match; no wallet was created")
        if len(wallet_password) < 12:
            raise NetworkError("Use a Monero wallet password of at least 12 characters")
        client.create_wallet(name, wallet_password, language="English")
        address = client.get_address()
    except (ConfigError, NetworkAccessDenied, NetworkError, OSError, ValueError) as exc:
        console.print(f"[red]Monero wallet creation failed:[/] {escape(str(exc))}")
        raise typer.Exit(code=1) from exc
    console.print(Panel.fit(
        f"[green]Monero wallet created by the official local wallet RPC.[/]\n"
        f"Wallet name: {escape(name)}\nAddress: {escape(address)}\n"
        "The Monero seed and wallet file are managed by monero-wallet-rpc, not stored in Vaultsh's encrypted vault.",
        title="Monero wallet created", border_style="green",
    ))


@monero_app.command("open-wallet")
def monero_open_wallet(
    name: str = typer.Argument(..., help="Wallet filename within monero-wallet-rpc's configured wallet directory."),
    rpc_url: str = typer.Option("http://127.0.0.1:18082/json_rpc", "--rpc-url", help="Loopback monero-wallet-rpc URL."),
    config_path: Path = typer.Option(Path("./vaultsh.toml"), "--config", help="Config allowing wallet RPC calls."),
    allow_network: bool = typer.Option(False, "--allow-network", help="Authorize the local wallet RPC call."),
    rpc_username: str | None = typer.Option(None, "--rpc-username", help="Optional monero-wallet-rpc digest-auth user."),
) -> None:
    """Open a Monero wallet file managed by the locally running wallet RPC."""
    try:
        settings = _load_network_settings(config_path, allow_network)
        client = _monero_client(rpc_url, settings.request_timeout_seconds, rpc_username)
        wallet_password = typer.prompt("Monero wallet password", hide_input=True)
        client.open_wallet(name, wallet_password)
        address = client.get_address()
    except (ConfigError, NetworkAccessDenied, NetworkError, OSError, ValueError) as exc:
        console.print(f"[red]Monero wallet open failed:[/] {escape(str(exc))}")
        raise typer.Exit(code=1) from exc
    console.print(f"[green]Opened Monero wallet:[/] {escape(name)}\nAddress: {escape(address)}")


@monero_app.command("close-wallet")
def monero_close_wallet(
    rpc_url: str = typer.Option("http://127.0.0.1:18082/json_rpc", "--rpc-url", help="Loopback monero-wallet-rpc URL."),
    config_path: Path = typer.Option(Path("./vaultsh.toml"), "--config", help="Config allowing wallet RPC calls."),
    allow_network: bool = typer.Option(False, "--allow-network", help="Authorize the local wallet RPC call."),
    rpc_username: str | None = typer.Option(None, "--rpc-username", help="Optional monero-wallet-rpc digest-auth user."),
) -> None:
    """Close the currently open local Monero wallet through wallet RPC."""
    try:
        settings = _load_network_settings(config_path, allow_network)
        _monero_client(rpc_url, settings.request_timeout_seconds, rpc_username).close_wallet()
    except (ConfigError, NetworkAccessDenied, NetworkError, OSError, ValueError) as exc:
        console.print(f"[red]Monero wallet close failed:[/] {escape(str(exc))}")
        raise typer.Exit(code=1) from exc
    console.print("[green]Monero wallet closed.[/]")


@monero_app.command("address")
def monero_address(
    rpc_url: str = typer.Option("http://127.0.0.1:18082/json_rpc", "--rpc-url", help="Loopback monero-wallet-rpc URL."),
    config_path: Path = typer.Option(Path("./vaultsh.toml"), "--config", help="Config allowing wallet RPC calls."),
    allow_network: bool = typer.Option(False, "--allow-network", help="Authorize the local wallet RPC call."),
    rpc_username: str | None = typer.Option(None, "--rpc-username", help="Optional monero-wallet-rpc digest-auth user."),
) -> None:
    """Show the primary address from the locally opened Monero wallet."""
    try:
        settings = _load_network_settings(config_path, allow_network)
        address = _monero_client(rpc_url, settings.request_timeout_seconds, rpc_username).get_address()
    except (ConfigError, NetworkAccessDenied, NetworkError, OSError, ValueError) as exc:
        console.print(f"[red]Monero RPC failed:[/] {escape(str(exc))}")
        raise typer.Exit(code=1) from exc
    console.print(f"Monero primary address: {escape(address)}")
    console.print("Use `vaultsh qr ADDRESS` to show or save its public address QR.")


@monero_app.command("balance")
def monero_balance(
    rpc_url: str = typer.Option("http://127.0.0.1:18082/json_rpc", "--rpc-url", help="Loopback monero-wallet-rpc URL."),
    config_path: Path = typer.Option(Path("./vaultsh.toml"), "--config", help="Config allowing wallet RPC calls."),
    allow_network: bool = typer.Option(False, "--allow-network", help="Authorize the local wallet RPC call."),
    rpc_username: str | None = typer.Option(None, "--rpc-username", help="Optional monero-wallet-rpc digest-auth user."),
) -> None:
    """Show Monero balance from a locally running official wallet RPC service."""
    try:
        settings = _load_network_settings(config_path, allow_network)
        balance, unlocked = _monero_client(rpc_url, settings.request_timeout_seconds, rpc_username).get_balance()
    except (ConfigError, NetworkAccessDenied, NetworkError, OSError, ValueError) as exc:
        console.print(f"[red]Monero balance failed:[/] {escape(str(exc))}")
        raise typer.Exit(code=1) from exc
    console.print(f"Total: {format_xmr(balance)} XMR\nUnlocked: {format_xmr(unlocked)} XMR")
    console.print("[dim]Balance visibility depends on the node/wallet synchronization state.[/]")


@monero_app.command("send")
def monero_send(
    destination: str = typer.Option(..., "--to", help="Monero Mainnet destination address."),
    amount: str = typer.Option(..., "--amount", help="XMR amount, up to 12 decimal places."),
    rpc_url: str = typer.Option("http://127.0.0.1:18082/json_rpc", "--rpc-url", help="Loopback monero-wallet-rpc URL."),
    config_path: Path = typer.Option(Path("./vaultsh.toml"), "--config", help="Config allowing wallet RPC calls."),
    allow_network: bool = typer.Option(False, "--allow-network", help="Authorize wallet RPC and relay."),
    rpc_username: str | None = typer.Option(None, "--rpc-username", help="Optional monero-wallet-rpc digest-auth user."),
) -> None:
    """Prepare XMR transfer through monero-wallet-rpc, then relay only after typed confirmation."""
    try:
        settings = _load_network_settings(config_path, allow_network)
        client = _monero_client(rpc_url, settings.request_timeout_seconds, rpc_username)
        source = client.get_address()
        preview = client.prepare_transfer(destination=destination, amount=amount)
    except (ConfigError, NetworkAccessDenied, NetworkError, OSError, ValueError) as exc:
        console.print(f"[red]Monero transfer preparation failed:[/] {escape(str(exc))}")
        raise typer.Exit(code=1) from exc
    console.print(Panel(
        f"Network: Monero Mainnet\nFrom: {source}\nTo: {preview.destination}\n"
        f"Amount: {format_xmr(preview.amount_atomic)} XMR\nFee: {format_xmr(preview.fee_atomic)} XMR\n"
        f"Total debit: {format_xmr(preview.amount_atomic + preview.fee_atomic)} XMR\nTX hash: {preview.tx_hash}",
        title="Review XMR transaction", border_style="orange",
    ))
    console.print("[yellow]The Monero wallet RPC process creates/signs this transaction. Verify its configuration and daemon before confirming.[/]")
    if not _confirm_transfer(symbol="XMR", amount=format_xmr(preview.amount_atomic), destination=preview.destination, fee=format_xmr(preview.fee_atomic)):
        console.print("[dim]Cancelled. The transaction was not relayed.[/]")
        return
    try:
        tx_hash = client.relay_transfer(preview)
    except NetworkError as exc:
        console.print(f"[red]Monero relay failed:[/] {escape(str(exc))}")
        raise typer.Exit(code=1) from exc
    console.print(Panel.fit(f"[green]Transaction relayed.[/] TX hash: {tx_hash}", title="Monero payment", border_style="green"))


@app.command()
def version() -> None:
    """Print the installed Vaultsh version."""
    console.print(f"Vaultsh {__version__}")


if __name__ == "__main__":
    app()
