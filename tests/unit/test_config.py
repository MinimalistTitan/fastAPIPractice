from app.core.config import Settings


def test_default_database_url_uses_postgresql() -> None:
    settings = Settings()

    assert settings.database_url.startswith("postgresql+asyncpg://")
