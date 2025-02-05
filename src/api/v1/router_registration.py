from fastapi import FastAPI

from src.api.v1.user.main_router import router as main_router
from src.api.v1.user.router import router as users_router
from src.api.v1.auth.router import router as auth_router
from src.api.v1.department.router import router as department_router
from src.api.v1.overtime.router import router as overtime_router
from src.api.v1.day_off.router import router as day_off_router
from src.api.v1.organization.router import router as organization_router


def register_routers(app: FastAPI) -> None:
    """
    Register all API routers for the application.

    Args:
        app (FastAPI): The FastAPI application instance.
    """

    app.include_router(main_router)
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(department_router)
    app.include_router(overtime_router)
    app.include_router(day_off_router)
    app.include_router(organization_router)
