from httpx import AsyncClient
import pytest



# Ваши тесты
@pytest.mark.asyncio
async def test_create_department_success(async_client: AsyncClient):
    department_data = {
        "name": "Human 4",
        "description": "Responsible for managing employee relations and payroll.",
    }
    response = await async_client.post("/department/", json=department_data)
    print(response.json())
    # assert response.status_code == 201

# @pytest.mark.asyncio
# async def test_get_all_departments_success(async_client: AsyncClient):
#     response = await async_client.get("/department/")
#     assert response.status_code == 200
#     print(response.json())