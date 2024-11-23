from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient
from src.api.v1.auth.schemas import UserCreate, UserOut
from src.api.v1.auth.service import AuthService


# async def test_login(async_client: AsyncClient, async_db_session: AsyncSession):
#     email = "superuser@example.com"
#     password = "password123"
#     username = "superuser"
#     full_name = "Super User"
#     position = "superuser"
#     role = "moderator"

#     super_user = await AuthService(async_db_session).create_superuser(
#             UserCreate(
#                 username=username,
#                 full_name=full_name,
#                 position=position,
#                 role=role,
#                 email=email,
#                 password=password
#             )
#         )

    # Отправляем запрос на логин
    # response = await async_client.post(
    #     "/auth/login",
    #     data={"username": username, "password": password},
    #     headers={"Content-Type": "application/x-www-form-urlencoded"},
    # )

    # print(response.json())