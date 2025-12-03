from __future__ import annotations

from typing import Iterable, Sequence, Any


def print_header(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def print_table(headers: Sequence[str], rows: Iterable[Sequence[Any]]) -> None:
    headers = list(headers)
    rows = [list(map(str, row)) for row in rows]

    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def fmt(row: Sequence[str]) -> str:
        return " | ".join(cell.ljust(widths[i]) for i, cell in enumerate(row))

    print(fmt(headers))
    print("-" * (sum(widths) + 3 * (len(widths) - 1)))
    for row in rows:
        print(fmt(row))


def prompt_int(label: str) -> int:
    while True:
        try:
            return int(input(f"{label}: ").strip())
        except ValueError:
            print("Please enter a valid integer.")


def prompt_float(label: str) -> float:
    while True:
        try:
            return float(input(f"{label}: ").strip())
        except ValueError:
            print("Please enter a valid number.")


def prompt_str(label: str) -> str:
    return input(f"{label}: ").strip()
