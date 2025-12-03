# db.py
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# -------------------------------------------------------------------
# Database configuration
# -------------------------------------------------------------------

# Use SQLite for local development so we can move forward.
# This creates a file "apple_cli.db" in your project folder.
DEFAULT_DB_URL = "sqlite:///apple_cli.db"

# You can override this with APPLE_DB_URL to use MySQL later, e.g.:
#   export APPLE_DB_URL="mysql+pymysql://apple_user:apple_pass@localhost/apple_cli_db"
DATABASE_URL = os.getenv("APPLE_DB_URL", DEFAULT_DB_URL)

# SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    future=True,
    echo=False,      # set True if you want to see SQL
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)

# Base class for ORM models
Base = declarative_base()


# -------------------------------------------------------------------
# Session helper
# -------------------------------------------------------------------

@contextmanager
def get_session() -> Iterator[Session]:
    """
    Provide a transactional scope around a series of operations.

    Usage:
        from db import get_session
        with get_session() as session:
            session.add(obj)
    """
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()