from __future__ import annotations
from typing import List, Optional
from app.db import db
from app.domain.user import User

class UserService:
    @staticmethod
    def create_user(name: str, email: str) -> User:
        if not name or not name.strip():
            raise ValueError("Name is required.")
        if not email or not email.strip():
            raise ValueError("Email is required.")

        name = name.strip()
        email = email.strip().lower()

        existing = db.session.query(User).filter_by(email=email).first()
        if existing:
            raise ValueError("Email already in use.")

        user = User(name=name, email=email)

        try:
            db.session.add(user)
            db.session.commit()
            return user
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def get_user(user_id: int) -> Optional[User]:
        return db.session.get(User, user_id)

    @staticmethod
    def list_users() -> List[User]:
        return db.session.query(User).order_by(User.id).all()

    @staticmethod
    def delete_user(user_id: int) -> None:
        user = db.session.get(User, user_id)
        if user is None:
            raise ValueError("User not found.")

        try:
            db.session.delete(user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
