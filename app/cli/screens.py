from __future__ import annotations
from rich.console import Console

from app.cli.widgets import prompt_int, prompt_float, show_table, banner
import db
from app.services import auth_service, portfolio_service, market_service
from app.services.exceptions import AppError, PermissionError

console = Console()

# ─────────────────────────── Login / Main ───────────────────────────

def login_screen() -> None:
    while True:
        banner("Welcome")
        console.print("1) Login")
        console.print("2) Exit")
        choice = input("Select an option (1-2): ").strip()
        if choice == "2":
            console.print("[bold]Goodbye![/bold]")
            raise SystemExit(0)
        if choice == "1":
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            try:
                auth_service.login(username, password)
                console.print(f"[green]Logged in as {username}[/green]")
                main_menu()
            except AppError as e:
                console.print(f"[red]{e}[/red]")
        else:
            console.print("[red]Invalid option.[/red]")

def main_menu() -> None:
    while True:
        user = db.get_logged_in()
        if not user:
            return
        banner(f"Main Menu – {user.username}")
        console.print("1) Manage Users")
        console.print("2) Manage Portfolios")
        console.print("3) Marketplace")
        console.print("4) Logout")
        choice = input("Select an option (1-4): ").strip()
        try:
            if choice == "1":
                manage_users_menu()
            elif choice == "2":
                manage_portfolios_menu()
            elif choice == "3":
                marketplace_menu()
            elif choice == "4":
                auth_service.logout()
                console.print("[yellow]Logged out.[/yellow]")
                return
            else:
                console.print("[red]Invalid option.[/red]")
        except AppError as e:
            console.print(f"[red]{e}[/red]")

# ─────────────────────────── Users (Admin) ───────────────────────────

def manage_users_menu() -> None:
    try:
        auth_service.require_admin()
    except PermissionError as e:
        console.print(f"[red]{e}[/red]")
        return

    while True:
        banner("Manage Users (admin)")
        console.print("1) View Users")
        console.print("2) Add User")
        console.print("3) Delete User")
        console.print("4) Back")
        choice = input("Select an option (1-4): ").strip()

        if choice == "4":
            return

        if choice == "1":
            rows = [[u.first_name, u.last_name, u.username, "Yes" if u.is_admin else "No", f"{u.balance:.2f}"]
                    for u in db.all_users()]
            show_table("Users", ["First", "Last", "Username", "Admin", "Balance"], rows)
            continue

        if choice == "2":
            first = input("First name: ").strip()
            last = input("Last name: ").strip()
            username = input("Username: ").strip()
            if db.username_exists(username):
                console.print("[red]Username already exists.[/red]")
                continue
            password = input("Password: ").strip()
            balance = prompt_float("Initial balance: ")
            is_admin = input("Make admin? (y/N): ").strip().lower() == "y"
            from app.domain.user import User
            db.add_user(User(first_name=first, last_name=last, username=username,
                             password=password, balance=balance, is_admin=is_admin))
            console.print("[green]User created.[/green]")
            continue

        if choice == "3":
            username = input("Username to delete: ").strip()
            if username not in db.users:
                console.print("[red]User does not exist.[/red]")
                continue
            if username == "admin":
                console.print("[red]Cannot delete the admin account.[/red]")
                continue
            if db.get_user_portfolios(username):
                console.print("[red]This user has portfolios. Delete them first.[/red]")
                continue
            db.remove_user(username)
            console.print("[green]User deleted.[/green]")
            continue

        console.print("[red]Invalid option.[/red]")

# ─────────────────────────── Portfolios ───────────────────────────

def manage_portfolios_menu() -> None:
    user = db.get_logged_in()
    if not user:
        return

    while True:
        banner("Manage Portfolios")
        console.print("1) View portfolios")
        console.print("2) Create portfolio (add holdings now)")
        console.print("3) Delete portfolio")
        console.print("4) Harvest investment (SELL)")
        console.print("5) Liquidate entire portfolio")
        console.print("6) Back")
        choice = input("Select an option (1-6): ").strip()

        try:
            if choice == "1":
                _show_user_portfolios(user.username)

            elif choice == "2":
                name = input("Portfolio name: ").strip()
                desc = input("Portfolio description: ").strip()
                p = portfolio_service.create_portfolio(user.username, name, desc)
                console.print(f"[green]Portfolio #{p.id} created.[/green]")
                _initial_buys_flow(user.username, p.id)   # ← ALWAYS prompts after creation

            elif choice == "3":
                pid = prompt_int("Portfolio id to delete: ")
                portfolio_service.delete_portfolio(user.username, pid)
                console.print("[green]Portfolio deleted.[/green]")

            elif choice == "4":
                pid = prompt_int("Portfolio id: ")
                ticker = input("Ticker to sell: ").strip().upper()
                qty = prompt_int("Quantity to sell: ")
                price = prompt_float("Sale price: ")
                portfolio_service.harvest(user.username, pid, ticker, qty, price)
                console.print("[green]Investment sold.[/green]")

            elif choice == "5":
                pid = prompt_int("Portfolio id to liquidate: ")
                port = portfolio_service.get_portfolio(user.username, pid)
                if not port.holdings:
                    console.print("[yellow]Portfolio has no holdings.[/yellow]")
                else:
                    for inv in list(port.holdings):
                        price = prompt_float(f"Sale price for {inv.ticker} (qty {inv.quantity}): ")
                        portfolio_service.harvest(user.username, pid, inv.ticker, inv.quantity, price)
                    console.print(f"[green]Portfolio #{pid} fully liquidated.[/green]")

            elif choice == "6":
                return
            else:
                console.print("[red]Invalid option.[/red]")

        except AppError as e:
            console.print(f"[red]{e}[/red]")

def _initial_buys_flow(username: str, portfolio_id: int) -> None:
    """Interactive loop to add one or more initial positions right after creation."""
    console.print(f"[cyan]Add initial holdings to portfolio #{portfolio_id}. "
                  f"Press Enter on Ticker to finish.[/cyan]")
    while True:
        _show_securities()
        ticker = input("Ticker (blank to finish): ").strip().upper()
        if not ticker:
            break
        qty = prompt_int("Quantity: ")
        try:
            portfolio_service.buy(username, portfolio_id, ticker, qty)
            console.print(f"[green]Added {qty} {ticker} to portfolio #{portfolio_id}[/green]")
        except AppError as e:
            console.print(f"[red]{e}[/red]")

def _show_user_portfolios(username: str) -> None:
    items = portfolio_service.list_user_portfolios(username)
    if not items:
        console.print("[yellow]You don't have any portfolios yet.[/yellow]")
        return

    rows = [[p.id, p.name, p.description, sum(inv.quantity for inv in p.holdings)] for p in items]
    show_table("Your Portfolios", ["Id", "Name", "Description", "Total Positions"], rows)

    for p in items:
        if not p.holdings:
            continue
        rows = [[inv.ticker, inv.quantity, f"{inv.purchase_price:.2f}"] for inv in p.holdings]
        show_table(f"Holdings for {p.name} (#{p.id})", ["Ticker", "Qty", "Last Buy Price"], rows)

# ─────────────────────────── Marketplace ───────────────────────────

def marketplace_menu() -> None:
    user = db.get_logged_in()
    if not user:
        return

    while True:
        banner("Marketplace")
        console.print("1) View securities")
        console.print("2) Place Buy Order")
        console.print("3) Back")
        choice = input("Select an option (1-3): ").strip()

        try:
            if choice == "3":
                return
            if choice == "1":
                _show_securities()
                continue
            if choice == "2":
                pid = prompt_int("Portfolio id: ")
                ticker = input("Ticker: ").strip().upper()
                qty = prompt_int("Quantity: ")
                portfolio_service.buy(user.username, pid, ticker, qty)
                console.print("[green]Buy order executed.[/green]")
                continue
            console.print("[red]Invalid option.[/red]")
        except AppError as e:
            console.print(f"[red]{e}[/red]")

def _show_securities() -> None:
    secs = market_service.list_market_securities()
    rows = [[s.ticker, s.issuer, f"{s.price:.2f}"] for s in secs]
    show_table("Available Securities", ["Ticker", "Issuer", "Price"], rows)
