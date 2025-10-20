from __future__ import annotations
from typing import List
import db
from app.domain.portfolio import Portfolio
from app.domain.investment import Investment
from app.services.exceptions import ValidationError, NotFoundError

def list_user_portfolios(username: str) -> List[Portfolio]:
    return db.get_user_portfolios(username)

def create_portfolio(username: str, name: str, description: str) -> Portfolio:
    if not name.strip():
        raise ValidationError("Portfolio name cannot be empty.")
    pid = db.next_portfolio_id()
    p = Portfolio(id=pid, name=name.strip(), description=description.strip())
    items = db.get_user_portfolios(username)
    items.append(p)
    db.save_user_portfolios(username, items)
    return p

def delete_portfolio(username: str, portfolio_id: int) -> None:
    items = db.get_user_portfolios(username)
    target = next((p for p in items if p.id == portfolio_id), None)
    if not target:
        raise NotFoundError("Invalid portfolio id.")
    if target.holdings:
        raise ValidationError("Portfolio has holdings. Liquidate investments before deleting.")
    items = [p for p in items if p.id != portfolio_id]
    db.save_user_portfolios(username, items)

def buy(username: str, portfolio_id: int, ticker: str, qty: int) -> None:
    if qty <= 0:
        raise ValidationError("Quantity must be a positive integer.")
    sec = db.get_security(ticker)
    if not sec:
        raise NotFoundError("Invalid ticker symbol.")
    user = db.users[username]
    cost = sec.price * qty
    if user.balance < cost:
        raise ValidationError("Insufficient balance for this order.")
    user.balance -= cost
    items = db.get_user_portfolios(username)
    target = next((p for p in items if p.id == portfolio_id), None)
    if not target:
        raise NotFoundError("Invalid portfolio id.")
    target.add_or_update_investment(Investment(ticker=sec.ticker, quantity=qty, purchase_price=sec.price))
    db.save_user_portfolios(username, items)

def harvest(username: str, portfolio_id: int, ticker: str, qty: int, sale_price: float) -> None:
    if qty <= 0:
        raise ValidationError("Quantity must be a positive integer.")
    if sale_price <= 0:
        raise ValidationError("Sale price must be positive.")
    items = db.get_user_portfolios(username)
    target = next((p for p in items if p.id == portfolio_id), None)
    if not target:
        raise NotFoundError("Invalid portfolio id.")
    inv = target.find_investment(ticker)
    if not inv:
        raise NotFoundError("Investment not found in this portfolio.")
    if qty > inv.quantity:
        raise ValidationError("Quantity exceeds current holding.")
    proceeds = sale_price * qty
    db.users[username].balance += proceeds
    if qty == inv.quantity:
        target.remove_investment(inv.ticker)
    else:
        inv.quantity -= qty
    db.save_user_portfolios(username, items)
