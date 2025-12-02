# tests/test_user_service.py
from __future__ import annotations

import pytest

from app.services.user_service import UserService
from db import get_session
from app.domain.models import User


def test_list_users_includes_seed_user():
    users = UserService.list_users()
    emails = [u.email for u in users]
    assert "testuser@example.com" in emails


def test_create_user_success_and_persisted():
    user = UserService.create_user("New User", "newuser@example.com")
    assert isinstance(user, User)
    assert user.id is not None
    assert user.email == "newuser@example.com"

    # verify in DB
    with get_session() as session:
        db_user = session.get(User, user.id)
        assert db_user is not None
        assert db_user.email == "newuser@example.com"


def test_create_user_duplicate_email_raises():
    # "testuser@example.com" is seeded in conftest
    with pytest.raises(ValueError):
        UserService.create_user("Other", "testuser@example.com")


def test_create_user_requires_name_and_email():
    with pytest.raises(ValueError):
        UserService.create_user("", "abc@example.com")

    with pytest.raises(ValueError):
        UserService.create_user("Name", "")


def test_get_user_returns_user_and_none_for_invalid_id():
    users = UserService.list_users()
    existing = users[0]

    found = UserService.get_user(existing.id)
    assert found is not None
    assert found.id == existing.id

    not_found = UserService.get_user(999999)
    assert not_found is None
