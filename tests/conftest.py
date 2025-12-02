# tests/conftest.py
from __future__ import annotations

import os
import sys
from typing import Iterator

import pytest

# ---------------------------------------------------------------------------
# Ensure project root is on sys.path so "import db" and "import app.*" work
# ---------------------------------------------------------------------------

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ---------------------------------------------------------------------------
# Configure test database (separate from dev DB)
# ---------------------------------------------------------------------------

TEST_DB_URL = "sqlite:///test_apple_cli.db"
os.environ["APPLE_DB_URL"] = TEST_DB_URL

from db import Base, engine, get_session  # noqa: E402
import app.domain.models  # noqa: F401  # register models with Base
from app.domain.models import User, Security


@pytest.fixture(scope="session", autouse=True)
def setup_database() -> Iterator[None]:
    """Create a fresh test database and seed basic data once per test session."""
    db_path = "test_apple_cli.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Seed demo user + a couple of securities
    with get_session() as session:
        demo = User(name="Test User", email="testuser@example.com", is_admin=True)
        session.add(demo)

        securities = [
            Security(symbol="AAPL", name="Apple Inc.", category="STOCK", last_price=190.0),
            Security(symbol="MSFT", name="Microsoft Corp.", category="STOCK", last_price=380.0),
        ]
        session.add_all(securities)

    yield

    # Optional: clean up DB file after tests
    if os.path.exists(db_path):
        os.remove(db_path)
