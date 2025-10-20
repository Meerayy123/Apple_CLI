from __future__ import annotations
import db
from app.services.exceptions import AuthError, PermissionError
from app.domain.user import User

def login(username: str, password: str) -> User:
    if username not in db.users:
        raise AuthError("Invalid username or password.")
    user = db.users[username]
    if user.password != password:
        raise AuthError("Invalid username or password.")
    db.set_logged_in(user)
    return user

def logout() -> None:
    db.set_logged_in(None)

def require_admin() -> None:
    user = db.get_logged_in()
    if not user or not user.is_admin:
        raise PermissionError("You are not authorized to access this feature.")
