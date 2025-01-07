from fastapi import FastAPI
from .user.router import router as users_router
from .auth.router import router as auth_router
from .department.router import router as department_router
from .overtime.router import router as overtime_router
from .day_off.router import router as day_off_router


def register_routers(app: FastAPI) -> None:
    """
    Register all API routers for the application.

    Args:
        app (FastAPI): The FastAPI application instance.
    """

    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(department_router)
    app.include_router(overtime_router)
    app.include_router(day_off_router)
