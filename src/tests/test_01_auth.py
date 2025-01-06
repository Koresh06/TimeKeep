from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models import User, Department, Role, WorkSchedule
from api.v1.user.service import UserService
from api.v1.user.schemas import UserCreate


async def create_test_user(
    async_db_session: AsyncSession,
    created_department: Department,
    username="user",
    password="password123",
    role=Role.USER.value,
    work_schedule=WorkSchedule.DAILY.value,
) -> User:
    return await UserService(async_db_session).create(
        UserCreate(
            department_oid=created_department.get("oid"),
            username=username,
            full_name="User",
            position="user",
            role=role,
            work_schedule=work_schedule,
            password=password,
        )
    )


async def test_create_access_token(
    async_client: AsyncClient,
    created_department: Department,
    async_db_session: AsyncSession,
):
    user = await create_test_user(async_db_session, created_department)
    response = await async_client.post(
        "/auth/access-token",
        data={
            "username": user.username,
            "password": "password123",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert "access_token" in response.json()


async def test_login(
    async_client: AsyncClient,
    created_department: Department,
    async_db_session: AsyncSession,
):
    user = await create_test_user(async_db_session, created_department)
    response = await async_client.post(
        "/auth/login",
        data={
            "username": user.username,
            "password": "password123",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"] == response.cookies["access_token"]


async def test_login_incorrect_password(
    async_client: AsyncClient,
    created_department: Department,
    async_db_session: AsyncSession,
):
    user = await create_test_user(async_db_session, created_department)
    response = await async_client.post(
        "/auth/login",
        data={
            "username": user.username,
            "password": "wrongpassword",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


async def test_login_incorrect_username(
    async_client: AsyncClient,
    created_department: Department,
    async_db_session: AsyncSession,
):
    await create_test_user(async_db_session, created_department)
    response = await async_client.post(
        "/auth/login",
        data={
            "username": "wrongusername",
            "password": "password123",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"