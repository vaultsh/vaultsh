from io import StringIO

import pytest
from rich.console import Console
from rich.panel import Panel

from vaultsh.ui.panels import error_panel, info_panel, success_panel, warning_panel
from vaultsh.ui.prompts import confirm_sensitive_action, transaction_review_text


def test_panel_helpers_return_rich_panels() -> None:
    assert isinstance(info_panel("hello"), Panel)
    assert isinstance(warning_panel("watch out"), Panel)
    assert isinstance(error_panel("failed"), Panel)
    assert isinstance(success_panel("saved"), Panel)


def test_transaction_review_includes_all_fields() -> None:
    review = transaction_review_text(
        network="testnet", destination="address123", amount="0.01 BTC", fee="0.0001 BTC"
    )
    assert "testnet" in review
    assert "address123" in review
    assert "0.01 BTC" in review
    assert "0.0001 BTC" in review
    assert "not implemented" in review


def test_confirmation_helper_rejects_empty_action() -> None:
    console = Console(file=StringIO())
    with pytest.raises(ValueError, match="must not be empty"):
        confirm_sensitive_action("  ", console=console)
