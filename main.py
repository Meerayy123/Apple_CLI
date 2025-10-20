from __future__ import annotations
from rich.console import Console
from app.cli.screens import login_screen

console = Console()

def main() -> None:
    try:
        login_screen()
    except SystemExit:
        pass
    except Exception as ex:
        console.print(f"[red]Unexpected error: {ex}[/red]")

if __name__ == "__main__":
    main()
