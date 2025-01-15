import sys
sys.dont_write_bytecode = True

import uvicorn

from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
# from fastapi_admin.app import app as admin_app

from api.conf_static import configure_static
from api.v1.router_registration import register_routers
from api.error_handlers import http_exception_handler
from core.config import settings
from core.logging import setup_logging
from middlewares.notification.middleware import NotificationMiddleware
# from api.v1.admin.admin_app import lifespan


def create_app():
    app = FastAPI(
        title="TimeKeep",
        description="TimeKeep API",
        version="1.0",
        # lifespan=lifespan,
    )
    
    configure_static(app)
    register_routers(app)

    app.add_exception_handler(HTTPException, http_exception_handler)

    app.add_middleware(NotificationMiddleware)


    @app.get("/")
    async def index():
        return RedirectResponse(
            url="/auth/",
            status_code=status.HTTP_302_FOUND,
        )
    
    # app.mount("/admin", admin_app)

    return app


if __name__ == "__main__":
    try:
        setup_logging()
        uvicorn.run(
            app=create_app(),
            host=settings.api.host,
            port=settings.api.port,
        )
    except KeyboardInterrupt:
        print("Программа завершена пользователем")
