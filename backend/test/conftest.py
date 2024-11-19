import asyncio
import logging
from typing import AsyncGenerator
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, AsyncConnection, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from asgi_lifespan import LifespanManager
from src.main import app
from src.models import Base
from src.core.session import get_async_session
from src.core.config import settings

from src.models import Department


@pytest_asyncio.fixture(loop_scope="session", scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def engine():
    engine = create_async_engine(
    url=settings.db.construct_sqlalchemy_url(is_test=True),
    echo=False,
    pool_pre_ping=True,
    poolclass=NullPool,
)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def async_db_engine(engine):

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def async_db_session(async_db_engine):
    async_session = sessionmaker(
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
        bind=async_db_engine,
        class_=AsyncSession,
    )

    async with async_session() as session:
        await session.begin()

        yield session

        await session.rollback()


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    def override_get_db():
        yield async_db_session

    app.dependency_overrides[get_async_session] = override_get_db


    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as client:
            yield client



@pytest_asyncio.fixture(scope="function")
async def test_department(async_db_session: AsyncSession) -> AsyncGenerator[Department, None]:
    department = Department(
        name="Human test",
        description="Responsible for managing employee relations and payroll.",
    )

    async_db_session.add(department)
    await async_db_session.commit()

    yield department

    await async_db_session.rollback()




# @pytest_asyncio.fixture(scope="session")
# async def engine():
#     engine = create_async_engine(
#     url=settings.db.construct_sqlalchemy_url(is_test=True),
#     echo=False,
#     pool_pre_ping=True,
#     poolclass=NullPool,
# )
#     yield engine
#     await engine.dispose()


# @pytest_asyncio.fixture(loop_scope="session", scope="session")
# async def async_db_connection(engine):
#     """
#     Создание таблиц для каждого теста и удаление их после выполнения теста.
#     """
#     async with engine.begin() as conn:
#         print("Creating tables...")
#         await conn.run_sync(Base.metadata.create_all)  # Создаём таблицы
#         print("Tables created.")

#     yield engine  # Передаём движок в тесты

#     async with engine.begin() as conn:
#         print("Dropping tables...")
#         await conn.run_sync(Base.metadata.drop_all)  # Удаляем таблицы
#         print("Tables dropped.")
        
#     # Закрытие соединения после теста
#     await engine.dispose()  # Явное завершение соединения




# @pytest_asyncio.fixture(scope="function")
# async def async_db_session(async_db_connection: AsyncConnection):
#     async_session = sessionmaker(
#         expire_on_commit=False,
#         autocommit=False,
#         autoflush=False,
#         bind=async_db_connection,
#         class_=AsyncSession,
#     )
#     async with async_session() as session:
#         trans = await session.begin_nested()  # Используем savepoint для отката
#         try:
#             yield session
#         finally:
#             await trans.rollback()
#             await session.close()


# # Фикстура для тестового клиента
# @pytest_asyncio.fixture
# async def async_client():
#     # Переопределяем зависимость `get_async_session`
#     def override_get_db():
#         yield async_db_session

#     app.dependency_overrides[get_async_session] = override_get_db

#     async with LifespanManager(app):
#         async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as client:
#             yield client






