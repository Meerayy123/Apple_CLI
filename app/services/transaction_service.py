# app/services/transaction_service.py
from __future__ import annotations

from typing import List, Optional

from app.db import db
from app.domain.user import User
from app.domain.portfolio import Portfolio
from app.domain.security import Security
from app.domain.investment import Investment
from app.domain.transactions import Transaction, TransactionType


class TransactionService:
    """Service layer for buy/sell operations and history queries (Flask-SQLAlchemy)."""

    @staticmethod
    def buy_security(
        user_id: int,
        portfolio_id: int,
        symbol: str,
        quantity: float,
        price_override: Optional[float] = None,
        notes: Optional[str] = None,
    ) -> Investment:
        if quantity is None or quantity <= 0:
            raise ValueError("Quantity must be positive.")
        symbol = (symbol or "").strip().upper()
        if not symbol:
            raise ValueError("Symbol is required.")

        user = db.session.get(User, user_id)
        if user is None:
            raise ValueError("User not found.")

        portfolio = db.session.get(Portfolio, portfolio_id)
        if portfolio is None:
            raise ValueError("Portfolio not found.")
        if portfolio.user_id != user_id:
            raise ValueError("Portfolio does not belong to user.")

        security = db.session.query(Security).filter_by(symbol=symbol).first()
        if security is None:
            raise ValueError(f"Security not found: {symbol}")

        trade_price = float(price_override) if price_override is not None else float(security.price)

        position = (
            db.session.query(Investment).filter_by(portfolio_id=portfolio.id, security_id=security.id)
            .first()
        )

        try:
            if position is None:
                position = Investment(
                    portfolio_id=portfolio.id,
                    security_id=security.id,
                    quantity=quantity,
                    avg_price=trade_price,
                )
                db.session.add(position)
            else:
                total_qty = position.quantity + quantity
                new_avg = ((position.quantity * position.avg_price) + (quantity * trade_price)) / total_qty
                position.quantity = total_qty
                position.avg_price = new_avg

            tx = Transaction(
                user_id=user.id,
                portfolio_id=portfolio.id,
                security_id=security.id,
                tx_type=TransactionType.BUY,
                quantity=quantity,
                price=trade_price,
                notes=(notes[:255] if notes else None),
            )
            db.session.add(tx)

            db.session.commit()
            db.session.refresh(position)
            return position
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def sell_security(
        user_id: int,
        portfolio_id: int,
        symbol: str,
        quantity: float,
        price_override: Optional[float] = None,
        notes: Optional[str] = None,
    ) -> None:
        if quantity is None or quantity <= 0:
            raise ValueError("Quantity must be positive.")
        symbol = (symbol or "").strip().upper()
        if not symbol:
            raise ValueError("Symbol is required.")

        user = db.session.get(User, user_id)
        if user is None:
            raise ValueError("User not found.")

        portfolio = db.session.get(Portfolio, portfolio_id)
        if portfolio is None:
            raise ValueError("Portfolio not found.")
        if portfolio.user_id != user_id:
            raise ValueError("Portfolio does not belong to user.")

        security = db.session.query(Security).filter_by(symbol=symbol).first()
        if security is None:
            raise ValueError(f"Security not found: {symbol}")

        position = (
            db.session.query(Investment).filter_by(portfolio_id=portfolio.id, security_id=security.id)
            .first()
        )
        if position is None or position.quantity < quantity:
            raise ValueError("Not enough quantity to sell.")

        trade_price = float(price_override) if price_override is not None else float(security.price)

        try:
            position.quantity -= quantity
            if position.quantity == 0:
                db.session.delete(position)

            tx = Transaction(
                user_id=user.id,
                portfolio_id=portfolio.id,
                security_id=security.id,
                tx_type=TransactionType.SELL,
                quantity=quantity,
                price=trade_price,
                notes=(notes[:255] if notes else None),
            )
            db.session.add(tx)

            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    # -------------------
    # History queries
    # -------------------

    @staticmethod
    def transactions_for_user(user_id: int) -> List[Transaction]:
        return db.session.query(Transaction).filter_by(user_id=user_id).order_by(Transaction.timestamp.desc()).all()

    @staticmethod
    def transactions_for_portfolio(portfolio_id: int) -> List[Transaction]:
        return db.session.query(Transaction).filter_by(portfolio_id=portfolio_id).order_by(Transaction.timestamp.desc()).all()

    @staticmethod
    def transactions_for_security(symbol: str) -> List[Transaction]:
        symbol = (symbol or "").strip().upper()
        security = db.session.query(Security).filter_by(symbol=symbol).first()
        if security is None:
            return []
        return db.session.query(Transaction).filter_by(security_id=security.id).order_by(Transaction.timestamp.desc()).all()
