# app/services/portfolio_service.py
from __future__ import annotations

from typing import List, Optional

from db import get_session
from app.domain.models import User, Portfolio


class PortfolioService:
    """Service layer for working with portfolios."""

    @staticmethod
    def create_portfolio(user_id: int, label: str) -> Portfolio:
        """Create a portfolio for a given user."""
        if not label.strip():
            raise ValueError("Portfolio label is required.")

        with get_session() as session:
            owner = session.get(User, user_id)
            if owner is None:
                raise ValueError("User does not exist.")

            portfolio = Portfolio(label=label.strip(), owner=owner)
            session.add(portfolio)
            session.flush()
            session.refresh(portfolio)
            return portfolio

    @staticmethod
    def get_portfolio(portfolio_id: int) -> Optional[Portfolio]:
        """Fetch a portfolio by id."""
        with get_session() as session:
            return session.get(Portfolio, portfolio_id)

    @staticmethod
    def list_for_user(user_id: int) -> List[Portfolio]:
        """List all portfolios for a given user."""
        with get_session() as session:
            return (
                session.query(Portfolio)
                .filter(Portfolio.user_id == user_id)
                .order_by(Portfolio.id)
                .all()
            )
