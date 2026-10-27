"""Reusable Rich panels for a consistent terminal interface."""

from rich.panel import Panel
from rich.text import Text


def info_panel(message: str, *, title: str = "Info") -> Panel:
    """Create a neutral informational panel."""
    return Panel(Text(message), title=title, border_style="cyan")


def warning_panel(message: str, *, title: str = "Warning") -> Panel:
    """Create a visible warning panel."""
    return Panel(Text(message), title=title, border_style="yellow")


def error_panel(message: str, *, title: str = "Error") -> Panel:
    """Create an error panel without implying any operation succeeded."""
    return Panel(Text(message), title=title, border_style="red")


def success_panel(message: str, *, title: str = "Done") -> Panel:
    """Create a success panel for an operation that actually completed."""
    return Panel(Text(message), title=title, border_style="green")
