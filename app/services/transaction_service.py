# app/services/transaction_service.py
from __future__ import annotations

from typing import List, Optional

from db import get_session
from app.domain.models import (
    User,
    Portfolio,
    Security,
    Investment,
    Transaction,
    TransactionKind,
)


class TransactionService:
    """Service layer for placing orders and querying transaction history."""

    # ------------------------------------------------------------------
    # Core trading operations
    # ------------------------------------------------------------------

    @staticmethod
    def buy_security(
        user_id: int,
        portfolio_id: int,
        symbol: str,
        quantity: float,
        price_override: Optional[float] = None,
    ) -> Investment:
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")

        symbol = symbol.strip().upper()
        if not symbol:
            raise ValueError("Symbol is required.")

        with get_session() as session:
            user = session.get(User, user_id)
            portfolio = session.get(Portfolio, portfolio_id)
            security = (
                session.query(Security)
                .filter(Security.symbol == symbol)
                .first()
            )

            if user is None:
                raise ValueError("User not found.")
            if portfolio is None:
                raise ValueError("Portfolio not found.")
            if portfolio.user_id != user_id:
                raise ValueError("Portfolio does not belong to user.")
            if security is None:
                raise ValueError(f"Security not found: {symbol}")

            trade_price = price_override if price_override is not None else security.last_price

            position = (
                session.query(Investment)
                .filter(
                    Investment.portfolio_id == portfolio.id,
                    Investment.security_id == security.id,
                )
                .first()
            )

            if position is None:
                position = Investment(
                    portfolio_id=portfolio.id,
                    security_id=security.id,
                    quantity=quantity,
                    avg_cost=trade_price,
                )
                session.add(position)
            else:
                total_qty = position.quantity + quantity
                new_cost = (
                    position.quantity * position.avg_cost
                    + quantity * trade_price
                ) / total_qty

                position.quantity = total_qty
                position.avg_cost = new_cost

            tx = Transaction(
                kind=TransactionKind.BUY,
                quantity=quantity,
                price=trade_price,
                user_id=user.id,
                portfolio_id=portfolio.id,
                security_id=security.id,
            )
            session.add(tx)

            session.flush()
            session.refresh(position)
            return position

    @staticmethod
    def sell_security(
        user_id: int,
        portfolio_id: int,
        symbol: str,
        quantity: float,
        price_override: Optional[float] = None,
    ) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")

        symbol = symbol.strip().upper()
        if not symbol:
            raise ValueError("Symbol is required.")

        with get_session() as session:
            user = session.get(User, user_id)
            portfolio = session.get(Portfolio, portfolio_id)
            security = (
                session.query(Security)
                .filter(Security.symbol == symbol)
                .first()
            )

            if user is None:
                raise ValueError("User not found.")
            if portfolio is None:
                raise ValueError("Portfolio not found.")
            if portfolio.user_id != user_id:
                raise ValueError("Portfolio does not belong to user.")
            if security is None:
                raise ValueError(f"Security not found: {symbol}")

            position = (
                session.query(Investment)
                .filter(
                    Investment.portfolio_id == portfolio.id,
                    Investment.security_id == security.id,
                )
                .first()
            )

            if position is None or position.quantity < quantity:
                raise ValueError("Not enough quantity to sell.")

            trade_price = price_override if price_override is not None else security.last_price

            position.quantity -= quantity
            if position.quantity == 0:
                session.delete(position)

            tx = Transaction(
                kind=TransactionKind.SELL,
                quantity=quantity,
                price=trade_price,
                user_id=user.id,
                portfolio_id=portfolio.id,
                security_id=security.id,
            )
            session.add(tx)

    # ------------------------------------------------------------------
    # History queries
    # ------------------------------------------------------------------

    @staticmethod
    def transactions_for_user(user_id: int) -> List[Transaction]:
        with get_session() as session:
            return (
                session.query(Transaction)
                .filter(Transaction.user_id == user_id)
                .order_by(Transaction.at.desc())
                .all()
            )

    @staticmethod
    def transactions_for_portfolio(portfolio_id: int) -> List[Transaction]:
        with get_session() as session:
            return (
                session.query(Transaction)
                .filter(Transaction.portfolio_id == portfolio_id)
                .order_by(Transaction.at.desc())
                .all()
            )

    @staticmethod
    def transactions_for_security(symbol: str) -> List[Transaction]:
        symbol = symbol.strip().upper()
        with get_session() as session:
            security = (
                session.query(Security)
                .filter(Security.symbol == symbol)
                .first()
            )
            if security is None:
                return []
            return (
                session.query(Transaction)
                .filter(Transaction.security_id == security.id)
                .order_by(Transaction.at.desc())
                .all()
            )
