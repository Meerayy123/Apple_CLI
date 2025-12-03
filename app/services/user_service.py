# app/services/user_service.py
from __future__ import annotations

from typing import List, Optional

from db import get_session
from app.domain.models import User


class UserService:
    """Service layer for working with users."""

    @staticmethod
    def create_user(name: str, email: str, is_admin: bool = False) -> User:
        """Create a new user. Raises ValueError if email already exists."""
        if not name.strip():
            raise ValueError("Name is required.")
        if not email.strip():
            raise ValueError("Email is required.")

        with get_session() as session:
            existing = session.query(User).filter_by(email=email).first()
            if existing:
                raise ValueError("Email already in use.")

            user = User(name=name.strip(), email=email.strip(), is_admin=is_admin)
            session.add(user)
            session.flush()   # assign id
            session.refresh(user)
            return user

    @staticmethod
    def get_user(user_id: int) -> Optional[User]:
        """Fetch a user by id, or None if not found."""
        with get_session() as session:
            return session.get(User, user_id)

    @staticmethod
    def list_users() -> List[User]:
        """Return all users ordered by id."""
        with get_session() as session:
            return session.query(User).order_by(User.id).all()
