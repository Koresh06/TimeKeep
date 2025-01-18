

# Запуск FastAPI
start:
	$ uvicorn src.main:create_app

# Создание суперпользователя
create-superuser:
	$(PYTHON_CMD) -m $(CREATE_SUPERUSER_SCRIPT)
