from datetime import UTC, datetime
from uuid import UUID

import pytest

from app.modules.users.domain.entities import User
from app.modules.users.domain.errors import InvalidDisplayNameError, InvalidEmailError


def test_register_user_normalizes_domain_values() -> None:
    user_id = UUID("b7f7468b-a1ae-4bc2-b4d7-30d413a6f032")
    now = datetime(2026, 8, 1, tzinfo=UTC)
    source_system = "unit-test"

    user = User.register(
        email="  Person@Example.COM ",
        display_name="  Ada   Lovelace  ",
        user_id=user_id,
        now=now,
        source_system=source_system
    )

    assert user.id == user_id
    assert user.email == "Person@example.com"
    assert user.display_name == "Ada Lovelace"
    assert user.created_at == now
    assert user.source_system == source_system


def test_register_user_rejects_invalid_email() -> None:
    with pytest.raises(InvalidEmailError):
        User.register(email="not-an-email", display_name="Ada Lovelace", source_system="unit-test")


def test_register_user_rejects_invalid_display_name() -> None:
    with pytest.raises(InvalidDisplayNameError):
        User.register(email="ada@example.com", display_name="A", source_system="unit-test")
