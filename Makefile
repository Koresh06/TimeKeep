

# Запуск FastAPI
start:
	$ uvicorn --factory src.main:create_app --host $(API_HOST) --port $(API_PORT)

# Создание суперпользователя
create-superuser:
	$(PYTHON_CMD) -m $(CREATE_SUPERUSER_SCRIPT)
