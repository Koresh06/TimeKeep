# Запуск приложения
start:
	$ uvicorn --factory src.main:create_app --host $(API_HOST) --port $(API_PORT)

# Создание суперпользователя
create-superuser:
	$ python scripts/create_superuser.py
