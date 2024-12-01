import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from asgi_lifespan import LifespanManager
from src.main import app
from src.models import Base
from src.core.session import get_async_session
from src.core.config import settings



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


@pytest_asyncio.fixture(loop_scope="session", scope="session")
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


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    def override_get_db():
        yield async_db_session

    app.dependency_overrides[get_async_session] = override_get_db


    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as client:
            yield client


# @pytest.fixture(scope="session")
# async def test_department(async_db_session):
#     department = await DepartmentService(async_db_session).create(
#         department_create=DepartmentCreate(
#             name="Human 6",
#             description="Responsible for managing employee relations and payroll.",
#         )
#     )
#     return department


# @pytest.fixture(scope="session")
# async def test_user(async_db_session: AsyncSession, test_department: Department):
#     user = await UserService(async_db_session).create_user(
#         data=UserCreate(
#             department_oid=test_department.oid,
#             username="test_user",
#             full_name="Test User",
#             position="Developer",
#             role = "user",
#             password="test_password",
#         )
#     )
#     return user

# @pytest.fixture(scope="session")
# async def superuser_token(async_client: AsyncClient, async_db_session: AsyncSession, test_department: Department):
#     superuser = await UserService(async_db_session).create_user(
#         data=UserCreate(
#             department_oid=test_department.oid,
#             username="admin_user",
#             full_name="Admin User",
#             position="Administrator",
#             role = "moderator",
#             password="admin_password",
#         )
#     )
#     token_response = await async_client.post(
#         "/auth/login",
#         data={"username": superuser.username, "password": "admin_password"},
#     )
#     return token_response.cookies["access_token"]

# @pytest.fixture(scope="session")
# async def user_token(async_client: AsyncClient, test_user: User):
#     token_response = await async_client.post(
#         "/auth/login",
#         data={"username": test_user.username, "password": "test_password"},
#     )
#     return token_response.cookies["access_token"]



