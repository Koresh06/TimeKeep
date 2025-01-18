PYTHON_CMD = poetry run python
MAIN_SCRIPT = src/main.py
CREATE_SUPERUSER_SCRIPT = scripts.create_superuser

# Запуск FastAPI
start:
	$(PYTHON_CMD) $(MAIN_SCRIPT)

# Создание суперпользователя
create-superuser:
	$(PYTHON_CMD) -m $(CREATE_SUPERUSER_SCRIPT)
