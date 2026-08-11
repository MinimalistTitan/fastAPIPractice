from collections.abc import AsyncIterator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.config import Environment, Settings
from app.core.database import Base
from app.main import create_app


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    settings = Settings(
        environment=Environment.TEST,
        database_url="sqlite+aiosqlite://",
        log_level="CRITICAL",
        trusted_hosts=["testserver"],
    )
    engine = create_async_engine(
        settings.database_url,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    application = create_app(settings=settings, engine=engine)
    transport = ASGITransport(app=application)
    async with (
        application.router.lifespan_context(application),
        AsyncClient(transport=transport, base_url="http://testserver") as test_client,
    ):
        yield test_client
