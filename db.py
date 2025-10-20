from __future__ import annotations
from typing import Dict, List, Optional
from app.domain.user import User
from app.domain.portfolio import Portfolio
from app.domain.security import Security

logged_in_user: Optional[User] = None

users: Dict[str, User] = {
    "admin": User(first_name="System", last_name="Admin", username="admin", password="admin123", balance=0.0, is_admin=True)
}

portfolios: Dict[str, List[Portfolio]] = {"admin": []}

securities: Dict[str, Security] = {
    "AAPL": Security(ticker="AAPL", issuer="Apple Inc.", price=180.00),
    "MSFT": Security(ticker="MSFT", issuer="Microsoft Corp.", price=330.00),
    "NVDA": Security(ticker="NVDA", issuer="NVIDIA Corp.", price=850.00),
}

_next_portfolio_id: int = 1

def set_logged_in(user: Optional[User]) -> None:
    global logged_in_user
    logged_in_user = user

def get_logged_in() -> Optional[User]:
    return logged_in_user

def username_exists(username: str) -> bool:
    return username in users

def add_user(user: User) -> None:
    users[user.username] = user
    if user.username not in portfolios:
        portfolios[user.username] = []

def remove_user(username: str) -> None:
    users.pop(username, None)
    portfolios.pop(username, None)

def all_users() -> List[User]:
    return list(users.values())

def next_portfolio_id() -> int:
    global _next_portfolio_id
    pid = _next_portfolio_id
    _next_portfolio_id += 1
    return pid

def get_user_portfolios(username: str) -> List[Portfolio]:
    return portfolios.get(username, [])

def save_user_portfolios(username: str, items: List[Portfolio]) -> None:
    portfolios[username] = items

def get_security(ticker: str) -> Optional[Security]:
    return securities.get(ticker.upper())

def list_securities() -> List[Security]:
    return list(securities.values())
