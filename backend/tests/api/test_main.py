import pytest


def test_read_root(client):
    response = client.get("/")
    
    # Проверяем статус код
    assert response.status_code == 200
    
    # Проверяем содержимое ответа
    assert response.json() == {"Hello": "World"}
