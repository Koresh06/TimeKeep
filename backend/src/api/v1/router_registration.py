# app/api/v1/router_registration.py
from fastapi import FastAPI
from .user.router import router as users_router
# from .auth_2.router import router as auth_router
from .auth.router import router as auth_router
from .department.router import router as department_router
from .overtime.router import router as overtime_router

def register_routers(app: FastAPI) -> None:
    """Функция для регистрации всех роутеров в приложении."""
    
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(department_router)
    app.include_router(overtime_router)
