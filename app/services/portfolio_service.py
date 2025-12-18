# app/services/portfolio_service.py
from __future__ import annotations

from typing import List, Optional

from app.db import db
from app.domain.user import User
from app.domain.portfolio import Portfolio


class PortfolioService:
    """Service layer for working with portfolios (Flask-SQLAlchemy)."""

    @staticmethod
    def create_portfolio(user_id: int, name: str) -> Portfolio:
        if not name or not name.strip():
            raise ValueError("Portfolio name is required.")

        owner = db.session.get(User, user_id)
        if owner is None:
            raise ValueError("User does not exist.")

        portfolio = Portfolio(name=name.strip(), user_id=owner.id)

        try:
            db.session.add(portfolio)
            db.session.commit()
            db.session.refresh(portfolio)
            return portfolio
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def get_portfolio(portfolio_id: int) -> Optional[Portfolio]:
        return db.session.get(Portfolio, portfolio_id)

    @staticmethod
    def list_portfolios() -> List[Portfolio]:
        return Portfolio.query.order_by(Portfolio.id).all()

    @staticmethod
    def list_for_user(user_id: int) -> List[Portfolio]:
        return Portfolio.query.filter_by(user_id=user_id).order_by(Portfolio.id).all()

    @staticmethod
    def delete_portfolio(portfolio_id: int) -> None:
        portfolio = db.session.get(Portfolio, portfolio_id)
        if portfolio is None:
            raise ValueError("Portfolio not found.")

        try:
            db.session.delete(portfolio)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
