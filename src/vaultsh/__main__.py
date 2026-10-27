"""Run Vaultsh with ``python -m vaultsh``."""

from vaultsh.cli import app


def main() -> None:
    """Execute the Typer application."""
    app()


if __name__ == "__main__":
    main()
