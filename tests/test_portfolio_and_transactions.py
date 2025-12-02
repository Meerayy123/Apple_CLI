# tests/test_portfolio_and_transactions.py
from __future__ import annotations

import pytest

from app.services.user_service import UserService
from app.services.portfolio_service import PortfolioService
from app.services.transaction_service import TransactionService
from db import get_session
from app.domain.models import Portfolio, Investment, Transaction, TransactionKind


@pytest.fixture
def demo_user():
    users = UserService.list_users()
    assert users, "Expected at least one user from seed data."
    return users[0]


def test_create_portfolio_for_user_and_fetch(demo_user):
    p = PortfolioService.create_portfolio(demo_user.id, "My Test Portfolio")
    assert isinstance(p, Portfolio)
    assert p.user_id == demo_user.id

    # get_portfolio
    fetched = PortfolioService.get_portfolio(p.id)
    assert fetched is not None
    assert fetched.id == p.id

    # list_for_user
    user_portfolios = PortfolioService.list_for_user(demo_user.id)
    ids = [pf.id for pf in user_portfolios]
    assert p.id in ids

    # verify from DB
    with get_session() as session:
        db_portfolio = session.get(Portfolio, p.id)
        assert db_portfolio is not None
        assert db_portfolio.label == "My Test Portfolio"


def test_create_portfolio_requires_label(demo_user):
    with pytest.raises(ValueError):
        PortfolioService.create_portfolio(demo_user.id, "   ")


def test_create_portfolio_user_must_exist():
    with pytest.raises(ValueError):
        PortfolioService.create_portfolio(999999, "Bad User")


def test_buy_and_sell_creates_investment_and_transactions(demo_user):
    portfolio = PortfolioService.create_portfolio(demo_user.id, "Trading")

    # BUY 10 AAPL @ 200
    position = TransactionService.buy_security(
        demo_user.id, portfolio.id, "AAPL", 10, price_override=200.0
    )
    assert isinstance(position, Investment)
    assert position.quantity == pytest.approx(10.0)
    assert position.avg_cost == pytest.approx(200.0)

    # SELL 4 AAPL @ 210
    TransactionService.sell_security(
        demo_user.id, portfolio.id, "AAPL", 4, price_override=210.0
    )

    # Check position quantity reduced to 6
    with get_session() as session:
        db_pos = (
            session.query(Investment)
            .filter(
                Investment.portfolio_id == portfolio.id,
                Investment.security_id == position.security_id,
            )
            .first()
        )
        assert db_pos is not None
        assert db_pos.quantity == pytest.approx(6.0)

        # Check two transactions logged
        txs = (
            session.query(Transaction)
            .filter(Transaction.portfolio_id == portfolio.id)
            .order_by(Transaction.id)
            .all()
        )
        assert len(txs) == 2
        assert txs[0].kind == TransactionKind.BUY
        assert txs[1].kind == TransactionKind.SELL

    # Also hit the history helpers
    user_txs = TransactionService.transactions_for_user(demo_user.id)
    assert len(user_txs) >= 2

    port_txs = TransactionService.transactions_for_portfolio(portfolio.id)
    assert len(port_txs) == len(user_txs)  # all user txs are in this portfolio

    sec_txs = TransactionService.transactions_for_security("AAPL")
    assert len(sec_txs) >= 2


def test_sell_more_than_owned_raises_error(demo_user):
    portfolio = PortfolioService.create_portfolio(demo_user.id, "Risky")

    # Buy small quantity first
    TransactionService.buy_security(
        demo_user.id, portfolio.id, "MSFT", 2, price_override=300.0
    )

    # Attempt to sell more than owned
    with pytest.raises(ValueError):
        TransactionService.sell_security(
            demo_user.id, portfolio.id, "MSFT", 5, price_override=310.0
        )


def test_buy_and_sell_validate_inputs_and_error_paths(demo_user):
    portfolio = PortfolioService.create_portfolio(demo_user.id, "Validation")

    # Quantity must be > 0
    with pytest.raises(ValueError):
        TransactionService.buy_security(demo_user.id, portfolio.id, "AAPL", 0)

    with pytest.raises(ValueError):
        TransactionService.sell_security(demo_user.id, portfolio.id, "AAPL", 0)

    # Symbol required
    with pytest.raises(ValueError):
        TransactionService.buy_security(demo_user.id, portfolio.id, "   ", 1)

    # Unknown security
    with pytest.raises(ValueError):
        TransactionService.buy_security(demo_user.id, portfolio.id, "XXXX", 1)

    # Wrong portfolio/user combo
    other_user = UserService.create_user("Other", "other@example.com")
    other_portfolio = PortfolioService.create_portfolio(other_user.id, "Other P")

    with pytest.raises(ValueError):
        TransactionService.buy_security(
            demo_user.id, other_portfolio.id, "AAPL", 1
        )

    # transactions_for_security on unknown symbol should be empty
    assert TransactionService.transactions_for_security("ZZZZ") == []
