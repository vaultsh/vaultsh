"""Explicit confirmation helpers for future sensitive user actions."""

from rich.console import Console
from rich.prompt import Confirm
from rich.text import Text


def confirm_sensitive_action(
    action: str,
    *,
    console: Console | None = None,
    default: bool = False,
) -> bool:
    """Ask for deliberate confirmation; default to rejecting the action."""
    if not isinstance(action, str) or not action.strip():
        raise ValueError("action description must not be empty")
    if console is None:
        console = Console()
    # Build a Text object instead of interpolating untrusted text into Rich markup.
    prompt = Text.assemble(("Confirm: ", "bold yellow"), action.strip())
    return Confirm.ask(prompt, console=console, default=default)


def transaction_review_text(
    *, network: str, destination: str, amount: str, fee: str
) -> str:
    """Format transaction details for review; this function does not sign."""
    values = {"network": network, "destination": destination, "amount": amount, "fee": fee}
    for name, value in values.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be a non-empty string")
        if any(ord(char) < 32 or ord(char) == 127 for char in value):
            raise ValueError(f"{name} must not contain control characters")
    return (
        "Review transaction details carefully before proceeding:\n"
        f"Network: {network}\nDestination: {destination}\n"
        f"Amount: {amount}\nEstimated fee: {fee}\n\n"
        "Signing and broadcasting are not implemented in this pre-alpha build."
    )
