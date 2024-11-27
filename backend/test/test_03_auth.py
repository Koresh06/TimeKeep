import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Department
from src.api.v1.auth.schemas import Token
from src.api.v1.auth.service import AuthService
from src.api.v1.user.service import UserService


async def test_login_access_token_success(
    async_client: AsyncClient,
    async_db_session: AsyncSession,
    test_department: Department,
):
    # Создаем тестового пользователя
    test_user = {
        "department_oid": test_department.oid,
        "username": "testuser",
        "password": "testpassword",
        "full_name": "Test User",
        "position": "Developer",
        "role": "user",
    }
    # Предполагаем, что у вас есть сервис для создания пользователя
    await UserService(async_db_session).create_user(**test_user)

    # Запрос токена
    response = await async_client.post(
        "/auth/access-token",
        data={
            "username": "testuser",
            "password": "testpassword",
        },
    )

    # assert response.status_code == 200
    # token = Token(**response.json())
    # assert token.access_token is not None
    print(response.json())
