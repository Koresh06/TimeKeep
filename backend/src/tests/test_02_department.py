from httpx import AsyncClient


async def test_create_department(async_client: AsyncClient, superuser_cookie):
    token = async_client.cookies.get("access_token")

    headers = {"Authorization": f"Bearer {token}"}
    
    department_data = {
        "name": "Human 6",
        "description": "Responsible for managing employee relations and payroll.",
    }
    
    response = await async_client.post("/department/", json=department_data, headers=headers)
    assert response.status_code == 201

    department = response.json()
    assert department["name"] == "Human 6"
    assert department["description"] == "Responsible for managing employee relations and payroll."
