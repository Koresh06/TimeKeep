import pytest
from httpx import AsyncClient
from fastapi import status

from src.api.v1.user.schemas import UserOut


# async def test_login_success(async_client: AsyncClient, test_user: UserOut):
#     # test_user должен быть создан заранее (например, через фикстуру)
#     response = await async_client.post(
#         "/access-token",
#         data={"username": test_user.username, "password": "test_password"}
#     )
#     # assert response.status_code == status.HTTP_200_OK
#     # assert "access_token" in response.cookies
#     print(response.json())


# async def test_login_invalid_credentials(async_client: AsyncClient):
#     response = await async_client.post(
#         "/access-token",
#         data={"username": "invalid_user", "password": "wrong_password"}
#     )
#     assert response.status_code == status.HTTP_401_UNAUTHORIZED
#     assert response.json()["detail"] == "Invalid credentials"



async def test_register_user_as_superuser(async_client: AsyncClient, superuser_token):
    response = await async_client.post(
        "/register",
        headers={"Authorization": f"Bearer {superuser_token}"},
        json={
            "username": "new_user",
            "full_name": "New User",
            "password": "password123",
            "position": "Developer",
            "role": "USER"
        }
    )
    print(response.json())
    # assert response.status_code == status.HTTP_201_CREATED
    # data = response.json()
    # assert data["username"] == "new_user"
    # assert data["role"] == "USER"


# async def test_register_user_as_non_superuser(async_client: AsyncClient, user_token):
#     response = await async_client.post(
#         "/register",
#         headers={"Authorization": f"Bearer {user_token}"},
#         json={
#             "username": "new_user",
#             "full_name": "New User",
#             "password": "password123",
#             "position": "Developer",
#             "role": "USER"
#         }
#     )
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert response.json()["detail"] == "The user doesn't have enough privileges"


# async def test_register_user_without_auth(async_client: AsyncClient):
#     response = await async_client.post(
#         "/register",
#         json={
#             "username": "new_user",
#             "full_name": "New User",
#             "password": "password123",
#             "position": "Developer",
#             "role": "USER"
#         }
#     )
#     assert response.status_code == status.HTTP_401_UNAUTHORIZED
#     assert response.json()["detail"] == "Could not validate credentials"
