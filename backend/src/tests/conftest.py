import asyncio
from typing import AsyncGenerator, Iterator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from asgi_lifespan import LifespanManager
from main import app
from core.session import get_async_session
from core.config import settings
from models import Base, Role, WorkSchedule, User, Department
from api.v1.user.service import UserService
from api.v1.user.schemas import UserCreate
from api.v1.auth.jwt import create_access_token


@pytest_asyncio.fixture(scope="function")
async def loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="function")
async def engine():
    engine = create_async_engine(
        url=settings.db.construct_sqlalchemy_url(is_test=True),
        echo=False,
        pool_pre_ping=True,
        poolclass=NullPool,
    )
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def async_db_engine(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def async_db_session(async_db_engine):
    async_session = sessionmaker(
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
        bind=async_db_engine,
        class_=AsyncSession,
    )

    async with async_session() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest_asyncio.fixture(scope="function")
async def async_client(async_db_session) -> AsyncGenerator[AsyncClient, None]:
    def override_get_db() -> Iterator[AsyncSession]:
        yield async_db_session

    app.dependency_overrides[get_async_session] = override_get_db

    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as client:
            yield client


@pytest_asyncio.fixture(scope="function")
async def test_superuser(async_client: AsyncClient, async_db_session: AsyncSession):
    superuser = await UserService(async_db_session).create_superuser(
        UserCreate(
            username="superuser",
            full_name="Superuser",
            position="superuser",
            role=Role.SUPERUSER.value,
            work_schedule=WorkSchedule.DAILY.value,
            password="password123",
        )
    )
    token = create_access_token(data={"user_oid": str(superuser.oid)})
    async_client.cookies.set("access_token", token)
    return token


@pytest_asyncio.fixture(scope="function")
async def created_department(async_client: AsyncClient, test_superuser):
    token = async_client.cookies.get("access_token")

    headers = {"Authorization": f"Bearer {token}"}
    
    department_data = {
        "name": "name 1",
        "description": "description 1",
    }
    
    response = await async_client.post("/department/", json=department_data, headers=headers)
    assert response.status_code == 201

    department = response.json()

    return department


@pytest_asyncio.fixture(scope="function")
async def test_moderator(async_client: AsyncClient, async_db_session: AsyncSession, created_department: Department):
    moderator = await UserService(async_db_session).create(
        UserCreate(
            department_oid=created_department.get("oid"),
            username="moderator",
            full_name="Moderator",
            position="moderator",
            role=Role.MODERATOR.value,
            work_schedule=WorkSchedule.DAILY.value,
            password="password123",
        )
    )
    token = create_access_token(data={"user_oid": str(moderator.oid)})
    async_client.cookies.set("access_token", token)
    return token


@pytest_asyncio.fixture(scope="function")
async def test_user(async_client: AsyncClient, async_db_session: AsyncSession, created_department: Department):
    user = await UserService(async_db_session).create(
        UserCreate(
            department_oid=created_department.get("oid"),
            username="user",
            full_name="User",
            position="user",
            role=Role.USER.value,
            work_schedule=WorkSchedule.DAILY.value,
            password="password123",
        )
    )
    token = create_access_token(data={"user_oid": str(user.oid)})
    async_client.cookies.set("access_token", token)
    return token
