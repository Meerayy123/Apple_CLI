from __future__ import annotations
from typing import Iterable
from rich.console import Console
from rich.table import Table

# local console for helper messages/tables
console = Console()

def prompt_int(message: str) -> int:
    while True:
        try:
            return int(input(message))
        except ValueError:
            console.print("[red]Please enter a valid integer.[/red]")

def prompt_float(message: str) -> float:
    while True:
        try:
            return float(input(message))
        except ValueError:
            console.print("[red]Please enter a valid number.[/red]")

def show_table(title: str, headers: Iterable[str], rows: Iterable[Iterable[object]]) -> None:
    table = Table(title=title)
    for h in headers:
        table.add_column(str(h))
    for row in rows:
        table.add_row(*[str(x) for x in row])
    console.print(table)

def banner(text: str) -> None:
    console.rule(f"[bold]{text}[/bold]")
