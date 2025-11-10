# Terminal UI helpers using Rich and prompt_toolkit.
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.json import JSON
from rich.live import Live
from rich.spinner import Spinner
from rich.table import Table

from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from typing import Dict, Any

console = Console()
session = PromptSession()

style = Style.from_dict({
    "prompt": "bold cyan"
})

from .utils import beautify_value

from typing import Any, Dict
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def render_result_card(result: Dict[str, Any], detected_type: str) -> None:
    def add_items_to_table(table: Table, data: Any, parent_key=""):
        if isinstance(data, dict):
            for k, v in data.items():
                full_key = f"{parent_key}.{k}" if parent_key else k
                add_items_to_table(table, v, full_key)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                full_key = f"{parent_key}[{i}]"
                add_items_to_table(table, item, full_key)
        else:
            display_key = beautify_value(parent_key)
            if isinstance(data, bool): data_str = "[green]True[/]" if data else "[red]False[/]"
            elif data is None: data_str = "[grey]None[/]"
            else: data_str = str(data)
            table.add_row(display_key, data_str)

    table = Table.grid(expand=True)
    table.add_column(justify="left", ratio=1)
    table.add_column(justify="right", ratio=2)
    table.add_row("Detected type", f"{detected_type}")
    add_items_to_table(table, result)
    console.print(Panel(table, title="Dymo Validation Result", subtitle="Press r to re-run, j to JSON."))

def render_error(message: str) -> None:
    # Render an error panel to the terminal.
    console.print(Panel(f"[bold red]{message}[/bold red]", title="Error", subtitle="Check your API key and network."))

async def show_loader_and_call(coro, *args, **kwargs):
    # Show a spinner while awaiting an async call and return result.
    with Live(Spinner("dots", text="Validating..."), refresh_per_second=12, console=console):
        return await coro(*args, **kwargs)

def render_json_toggle(data: Dict[str, Any]) -> None:
    # Show JSON representation with rich JSON viewer.
    console.print(Panel(JSON.from_data(data), title="Raw JSON"))

from prompt_toolkit import Application
from prompt_toolkit.layout import Layout, HSplit
from prompt_toolkit.widgets import TextArea, Label, Box, Frame
from prompt_toolkit.key_binding import KeyBindings

def interactive_input(prompt_text: str = "Enter value to validate") -> str:
    """
    Display a rectangle where the user can type and edit inside it.
    Returns the input string when Enter is pressed.
    """
    result = {"text": ""} # mutable container to store input

    # Text input area
    input_area = TextArea(
        multiline=False,
        prompt=f"",
        style="class:input-area",
    )

    # Label above input
    label = Label(f"{prompt_text}:", style="bold cyan")

    # Frame/Box around input
    frame = Frame(HSplit([label, input_area]), title="Dymo CLI Input", style="class:frame")

    # Key bindings
    kb = KeyBindings()

    @kb.add("c-c")
    @kb.add("c-q")
    def exit_(event):
        # Exit without saving
        event.app.exit(result=None)

    @kb.add("enter")
    def accept(event):
        # Save input and exit
        result["text"] = input_area.text
        event.app.exit(result=result["text"])

    # Build application
    app = Application(layout=Layout(frame), key_bindings=kb, full_screen=False)

    # Run app
    text = app.run()
    return text