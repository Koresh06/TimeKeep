# Переменные
PYTHON_CMD = python
MAIN_SCRIPT = backend/src/main.py

# Запуск FastAPI
start:
	$(PYTHON_CMD) $(MAIN_SCRIPT)
