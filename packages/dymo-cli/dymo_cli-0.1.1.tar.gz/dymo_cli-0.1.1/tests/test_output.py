# Basic output formatting tests with mocked results.
from dymo_cli.ui import render_result_card
import pytest
from rich.console import Console
from rich.panel import Panel

def test_render_result_card_snapshot(capsys):
    console = Console(record=True)
    result = {
        "verdict": "clean",
        "meta": {"mx": "exists", "score": 0.92},
    }
    render_result_card(result, "email")
    assert True