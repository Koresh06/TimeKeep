# app/api/v1/router_registration.py
from fastapi import FastAPI
from .user.router import router as users_router
from .auth.router import router as auth_router

def register_routers(app: FastAPI) -> None:
    """Функция для регистрации всех роутеров в приложении."""
    
    app.include_router(users_router, prefix="/users", tags=["users"])
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
