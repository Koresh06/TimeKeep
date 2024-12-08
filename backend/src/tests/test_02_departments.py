from uuid import uuid4
from httpx import AsyncClient
from models import Department, User


async def test_create_department(async_client: AsyncClient, created_department: Department):
    assert created_department["name"] == created_department["name"]
    assert created_department["description"] == created_department["description"]


async def test_create_department_invalid_data(async_client: AsyncClient, test_superuser: User):
    token = async_client.cookies.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    invalid_department_data = {
        "name": 1, 
        "description": "Valid description",
    }

    response = await async_client.post("/department/", json=invalid_department_data, headers=headers)
    assert response.status_code == 422


async def test_create_department_unauthorized(async_client: AsyncClient):
    department_data = {
        "name": "HR",
        "description": "Responsible for managing employee relations",
    }

    response = await async_client.post("/department/", json=department_data)

    assert response.status_code == 401  
    assert response.json()["detail"] == "Not authenticated"



async def test_get_all_departments(async_client: AsyncClient, test_superuser, created_department: Department):
    token = async_client.cookies.get("access_token")

    headers = {"Authorization": f"Bearer {token}"}
    
    response = await async_client.get("/department/", headers=headers)
    assert response.status_code == 200

    departments = response.json()
    assert len(departments) > 0

    for department in departments:
        assert department["name"] ==  created_department["name"]
        assert department["description"] == created_department["description"]


async def test_get_one_department_not_found(async_client: AsyncClient, test_superuser):
    token = async_client.cookies.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    invalid_oid = str(uuid4())

    response = await async_client.get(f"/department/{invalid_oid}", headers=headers)
    assert response.status_code == 404  

    assert response.json()["detail"] == f"Department {invalid_oid} not found!" 


async def test_get_one_department(async_client: AsyncClient, test_superuser, created_department: Department):
    token = async_client.cookies.get("access_token")

    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.get(f"/department/{created_department.get('oid')}", headers=headers)
    assert response.status_code == 200

    department = response.json()
    assert department["name"] ==  created_department["name"]
    assert department["description"] == created_department["description"]


async def test_modify_department(async_client: AsyncClient, test_superuser, created_department: Department):
    token = async_client.cookies.get("access_token")

    headers = {"Authorization": f"Bearer {token}"}

    department_data = {
        "name": "name 2",
    }
    
    response = await async_client.patch(f"/department/{created_department.get('oid')}", json=department_data, headers=headers)
    assert response.status_code == 200

    department = response.json()
    assert department["name"] == department_data["name"]


async def test_modify_department_forbidden(async_client: AsyncClient, test_user: User, created_department: Department):
    token = async_client.cookies.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    department_data = {
        "name": "New name",
    }

    response = await async_client.patch(f"/department/{created_department.get('oid')}", json=department_data, headers=headers)
    assert response.status_code == 403 
    assert response.json()["detail"] == "Not enough permissions"



async def test_replace_department(async_client: AsyncClient, test_superuser, created_department: Department):
    token = async_client.cookies.get("access_token")

    headers = {"Authorization": f"Bearer {token}"}

    department_data = {
        "name": "name 3",
        "description": "description 3",
    }
    
    response = await async_client.put(f"/department/{created_department.get('oid')}", json=department_data, headers=headers)
    assert response.status_code == 200

    department = response.json()
    assert department["name"] == department_data["name"]
    assert department["description"] == department_data["description"]


async def test_delete_department(async_client: AsyncClient, test_superuser, created_department: Department):
    token = async_client.cookies.get("access_token")

    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.delete(f"/department/{created_department.get('oid')}", headers=headers)
    assert response.status_code == 204


