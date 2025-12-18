from __future__ import annotations

from app.services.user_service import UserService
from app.services.portfolio_service import PortfolioService
from app.services.transaction_service import TransactionService
from app.cli.widgets import (
    print_header,
    print_table,
    prompt_int,
    prompt_float,
    prompt_str,
)


def main_menu() -> None:
    """Top-level menu for the CLI application."""
    while True:
        print_header("Apple CLI - Portfolio Manager")
        print("1) List users")
        print("2) Create user")
        print("3) Select user")
        print("4) Exit")
        choice = input("Select an option (1-4): ").strip()

        if choice == "1":
            show_users()
        elif choice == "2":
            create_user()
        elif choice == "3":
            select_user_menu()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, please try again.")


# --------------------------- User screens ---------------------------

def show_users() -> None:
    users = UserService.list_users()
    if not users:
        print("No users found.")
        return

    print_header("Users")
    rows = [(u.id, u.name, u.email, "yes" if u.is_admin else "no") for u in users]
    print_table(["ID", "Name", "Email", "Admin"], rows)


def create_user() -> None:
    print_header("Create User")
    name = prompt_str("Name")
    email = prompt_str("Email")

    try:
        user = UserService.create_user(name, email)
        print(f"Created user with id={user.id}")
    except ValueError as e:
        print(f"Error: {e}")


def select_user_menu() -> None:
    show_users()
    user_id = prompt_int("Enter user ID to manage (0 to cancel)")
    if user_id == 0:
        return

    user = UserService.get_user(user_id)
    if not user:
        print("User not found.")
        return

    user_menu(user_id, user.name)


def user_menu(user_id: int, user_name: str) -> None:
    while True:
        print_header(f"User: {user_name} (id={user_id})")
        print("1) List portfolios")
        print("2) Create portfolio")
        print("3) Select portfolio")
        print("4) View all transactions for user")
        print("5) Back to main menu")

        choice = input("Select an option (1-5): ").strip()

        if choice == "1":
            show_portfolios(user_id)
        elif choice == "2":
            create_portfolio(user_id)
        elif choice == "3":
            select_portfolio_menu(user_id)
        elif choice == "4":
            show_user_transactions(user_id)
        elif choice == "5":
            break
        else:
            print("Invalid choice, please try again.")


# ------------------------ Portfolio screens ------------------------

def show_portfolios(user_id: int) -> None:
    portfolios = PortfolioService.list_for_user(user_id)
    if not portfolios:
        print("No portfolios found.")
        return

    print_header("Portfolios")
    rows = [(p.id, p.label) for p in portfolios]
    print_table(["ID", "Label"], rows)


def create_portfolio(user_id: int) -> None:
    print_header("Create Portfolio")
    label = prompt_str("Portfolio label")

    try:
        p = PortfolioService.create_portfolio(user_id, label)
        print(f"Created portfolio with id={p.id}")
    except ValueError as e:
        print(f"Error: {e}")


def select_portfolio_menu(user_id: int) -> None:
    portfolios = PortfolioService.list_for_user(user_id)
    if not portfolios:
        print("No portfolios found.")
        return

    show_portfolios(user_id)
    portfolio_id = prompt_int("Enter portfolio ID (0 to cancel)")
    if portfolio_id == 0:
        return

    portfolio = PortfolioService.get_portfolio(portfolio_id)
    if not portfolio or portfolio.user_id != user_id:
        print("Portfolio not found or does not belong to this user.")
        return

    portfolio_menu(user_id, portfolio_id, portfolio.label)


def portfolio_menu(user_id: int, portfolio_id: int, label: str) -> None:
    while True:
        print_header(f"Portfolio: {label} (id={portfolio_id})")
        print("1) Buy security")
        print("2) Sell security")
        print("3) View portfolio transactions")
        print("4) Back to user menu")

        choice = input("Select an option (1-4): ").strip()

        if choice == "1":
            buy_security_screen(user_id, portfolio_id)
        elif choice == "2":
            sell_security_screen(user_id, portfolio_id)
        elif choice == "3":
            show_portfolio_transactions(portfolio_id)
        elif choice == "4":
            break
        else:
            print("Invalid choice, please try again.")


# --------------------- Trading + transactions ----------------------

def buy_security_screen(user_id: int, portfolio_id: int) -> None:
    print_header("Buy Security")
    symbol = prompt_str("Symbol (e.g., AAPL)")
    qty = prompt_float("Quantity")
    price_input = prompt_str("Price override (blank to use last_price)")
    price = float(price_input) if price_input else None

    try:
        pos = TransactionService.buy_security(user_id, portfolio_id, symbol, qty, price)
        print(
            f"Buy executed. New position quantity={pos.quantity}, "
            f"avg_cost={pos.avg_cost:.2f}"
        )
    except ValueError as e:
        print(f"Error: {e}")


def sell_security_screen(user_id: int, portfolio_id: int) -> None:
    print_header("Sell Security")
    symbol = prompt_str("Symbol (e.g., AAPL)")
    qty = prompt_float("Quantity")
    price_input = prompt_str("Price override (blank to use last_price)")
    price = float(price_input) if price_input else None

    try:
        TransactionService.sell_security(user_id, portfolio_id, symbol, qty, price)
        print("Sell executed successfully.")
    except ValueError as e:
        print(f"Error: {e}")


def show_user_transactions(user_id: int) -> None:
    txs = TransactionService.transactions_for_user(user_id)
    if not txs:
        print("No transactions for this user.")
        return

    print_header(f"Transactions for user_id={user_id}")
    rows = [
        (t.id, t.portfolio_id, t.security_id, t.kind.value, t.quantity, t.price, t.at)
        for t in txs
    ]
    print_table(
        ["ID", "Portfolio", "Security", "Type", "Qty", "Price", "Timestamp"],
        rows,
    )


def show_portfolio_transactions(portfolio_id: int) -> None:
    txs = TransactionService.transactions_for_portfolio(portfolio_id)
    if not txs:
        print("No transactions for this portfolio.")
        return

    print_header(f"Transactions for portfolio_id={portfolio_id}")
    rows = [
        (t.id, t.user_id, t.security_id, t.kind.value, t.quantity, t.price, t.at)
        for t in txs
    ]
    print_table(
        ["ID", "User", "Security", "Type", "Qty", "Price", "Timestamp"],
        rows,
    )
