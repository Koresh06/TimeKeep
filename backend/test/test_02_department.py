from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import pytest

from src.models.department import Department


# async def test_create_department(async_client: AsyncClient, async_db_session: AsyncSession):
#     department_data = {
#         "name": "Human 6",
#         "description": "Responsible for managing employee relations and payroll.",
#     }
#     response = await async_client.post("/department/", json=department_data)
#     assert response.status_code == 201


# async def test_get_all_departments(async_client: AsyncClient, async_db_session: AsyncSession):
#     response = await async_client.get("/department/")
#     assert response.status_code == 200

#     response_data = response.json()
#     assert len(response_data) > 0

#     for department in response_data:
#         assert "name" in department


# async def test_get_one_department(async_client: AsyncClient, async_db_session: AsyncSession, test_department: Department):
#     response = await async_client.get(f"/department/{test_department.id}")
#     assert response.status_code == 200

#     response_data = response.json()
#     assert test_department.name == response_data["name"]
#     assert test_department.description == response_data["description"]