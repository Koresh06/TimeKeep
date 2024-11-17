import pytest_asyncio
from typing import Iterator

from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    AsyncConnection,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker
from asgi_lifespan import LifespanManager

from src.core.config import settings
from src.main import app
from src.core.session import get_async_session
from src.models import Base



engine = create_async_engine(
    url=settings.db.construct_sqlalchemy_url(is_test=True),
    echo=False,
    pool_pre_ping=True,
    poolclass=NullPool,
)

@pytest_asyncio.fixture(scope="session")
async def async_db_connection():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def async_db_session(async_db_connection: AsyncConnection):
    async_session = sessionmaker(
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
        bind=async_db_connection,
        class_=AsyncSession,
    )

    async with async_session() as session:
        transaction = await session.begin()

        yield session

        await transaction.rollback()
        await session.close()


@pytest_asyncio.fixture(scope="function")
async def async_client(async_db_session: AsyncSession):
    def override_get_db():
        yield async_db_session

    app.dependency_overrides[get_async_session] = override_get_db

    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as client: 
            yield client







