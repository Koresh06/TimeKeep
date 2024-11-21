from httpx import AsyncClient
from fastapi_users.router.common import ErrorCode


# async def test_register_user_success(async_client: AsyncClient, test_superuser):
#     """Тест успешной регистрации нового пользователя."""
#     new_user_data = {
#         "email": "korets-24@mail.ru",
#         "password": "11111111",
#         "is_active": True,
#         "is_superuser": False,
#         "is_verified": False,
#         "username": "koresh",
#         "department_id": "b1213b00-940d-4a66-88e1-50313d077745",
#         "role": "moderator"
#     }
#     headers = {"Authorization": f"Bearer {test_superuser['token']}"}
#     response = await async_client.post("/auth/register", json=new_user_data, headers=headers)
    
#     assert response.status_code == 201
#     response_data = response.json()
#     assert response_data["email"] == new_user_data["email"]
#     assert response_data["is_superuser"] == new_user_data["is_superuser"]


# async def test_register_user_already_exists(async_client: AsyncClient, test_superuser):
#     """Тест на ошибку при попытке регистрации пользователя с существующим email."""
#     existing_user_data = {
#         "email": "superuser@example.com",  # Используем email суперпользователя
#         "password": "newpassword",
#         "is_superuser": False,
#     }
#     headers = {"Authorization": f"Bearer {test_superuser['token']}"}
#     response = await async_client.post("/auth/register", json=existing_user_data, headers=headers)

#     assert response.status_code == 400
#     response_data = response.json()
#     assert response_data["detail"] == ErrorCode.REGISTER_USER_ALREADY_EXISTS


# async def test_register_invalid_password(async_client: AsyncClient, test_superuser):
#     """Тест на ошибку при попытке регистрации с некорректным паролем."""
#     invalid_user_data = {
#         "email": "invalidpassword@example.com",
#         "password": "12",  # Пароль слишком короткий
#         "is_superuser": False,
#     }
#     headers = {"Authorization": f"Bearer {test_superuser['token']}"}
#     response = await async_client.post("/auth/register", json=invalid_user_data, headers=headers)

#     assert response.status_code == 400
#     response_data = response.json()
#     assert response_data["detail"]["code"] == ErrorCode.REGISTER_INVALID_PASSWORD
