import uuid
from httpx import AsyncClient

from models import User, Department, Role, WorkSchedule
from api.v1.user.service import UserService
from api.v1.user.schemas import UserCreate


async def test_unauthorized_user(async_client: AsyncClient):
    response = await async_client.get("/user/")
    assert response.status_code == 401 


async def test_register_user(
    async_client: AsyncClient, test_superuser: User, created_department: Department
):
    token = async_client.cookies.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.post(
        "/user/register",
        headers=headers,
        json={
            "department_oid": created_department.get("oid"),
            "username": "test_user",
            "full_name": "Test User",
            "position": "test_position",
            "role": Role.USER.value,
            "work_schedule": WorkSchedule.DAILY.value,
            "password": "test_password",
        },
    )

    assert response.status_code == 201

    user = response.json()

    assert user["username"] == "test_user"
    assert user["full_name"] == "Test User"
    assert user["position"] == "test_position"
    assert user["role"] == Role.USER.value
    assert user["work_schedule"] == WorkSchedule.DAILY.value


async def test_register_user_invalid_data(
    async_client: AsyncClient, test_superuser: User
):
    token = async_client.cookies.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.post(
        "/user/register",
        headers=headers,
        json={
            "username": "",
            "full_name": "",
            "position": "",
            "role": "INVALID_ROLE",
            "work_schedule": "INVALID_SCHEDULE",
            "password": "",
        },
    )

    assert response.status_code == 422


async def test_registe_permission_denied(async_client: AsyncClient, test_user: User):
    token = async_client.cookies.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.post(
        "/user/register",
        headers=headers,
        json={
            "username": "test_user",
            "full_name": "Test User",
            "position": "test_position",
            "role": Role.USER.value,
            "work_schedule": WorkSchedule.DAILY.value,
            "password": "test_password",
        },
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Not enough permissions"}


async def test_get_users(async_client: AsyncClient, test_moderator: User):
    token = async_client.cookies.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.get("/user/", headers=headers)
    assert response.status_code == 200

    users = response.json()

    assert len(users) > 0

    for user in users:
        assert "username" in user
        assert "full_name" in user
        assert "position" in user
        assert "role" in user


async def test_get_one_user(async_client: AsyncClient, test_moderator: User):
    token = async_client.cookies.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.get(f"/user/{test_moderator.oid}", headers=headers)
    assert response.status_code == 200

    user = response.json()

    assert test_moderator.oid == uuid.UUID(user.get("oid"))
    assert test_moderator.username == user.get("username")


async def test_get_one_user_not_found(async_client: AsyncClient, test_superuser: User):
    token = async_client.cookies.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.get(f"/user/{uuid.uuid4()}", headers=headers)
    assert response.status_code == 404  


async def test_get_me_user(async_client: AsyncClient, test_user: User):
    token = async_client.cookies.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.get("/user/me", headers=headers)
    assert response.status_code == 200

    user = response.json()

    assert test_user.oid == uuid.UUID(user.get("oid"))
    assert test_user.username == user.get("username")


async def test_patch_user(async_client: AsyncClient, test_superuser: User):
    token = async_client.cookies.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.patch(
        f"/user/{test_superuser.oid}",
        headers=headers,
        json={"full_name": "Updated name"},
    )

    assert response.status_code == 200

    user = response.json()

    assert user["full_name"] == "Updated name"


async def test_patch_user_invalid_data(
    async_client: AsyncClient, test_superuser: User
):
    token = async_client.cookies.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.patch(
        f"/user/{test_superuser.oid}",
        headers=headers,
        json={"full_name": 111},
    )

    assert response.status_code == 422


async def test_put_user(async_client: AsyncClient, test_superuser: User):
    token = async_client.cookies.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.put(
        f"/user/{test_superuser.oid}",
        headers=headers,
        json={
            "username": "test_user_update",
            "full_name": "Test User Update",
            "position": "test_position_update",
            "role": Role.USER.value,
            "work_schedule": WorkSchedule.DAILY.value,
            "password": "test_password",
        },
    )

    assert response.status_code == 200

    user = response.json()

    assert user["username"] == "test_user_update"
    assert user["full_name"] == "Test User Update"
    assert user["position"] == "test_position_update"


async def test_put_user_invalid_data(async_client: AsyncClient, test_superuser: User):
    token = async_client.cookies.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.put(
        f"/user/{test_superuser.oid}",
        headers=headers,
        json={
            "username": 123, 
            "full_name": 123,
            "position": 123,
            "role": "INVALID_ROLE",
            "work_schedule": "INVALID_SCHEDULE",
            "password": "",
        },
    )

    assert response.status_code == 422


async def test_delete_user(async_client: AsyncClient, test_superuser: User):
    token = async_client.cookies.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.delete(f"/user/{test_superuser.oid}", headers=headers)
    assert response.status_code == 204


async def test_delete_user_not_found(async_client: AsyncClient, test_superuser: User):
    token = async_client.cookies.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.delete(
        f"/user/{uuid.uuid4()}", headers=headers
    )
    assert response.status_code == 404 