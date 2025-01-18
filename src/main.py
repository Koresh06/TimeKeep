import sys
import os

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))


import uvicorn

from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse

from src.api.conf_static import configure_static
from src.api.v1.router_registration import register_routers
from src.api.error_handlers import http_exception_handler
from src.core.config import settings
from src.core.logging import setup_logging
from src.middlewares.notification.middleware import NotificationMiddleware


def create_app():
    app = FastAPI(
        title="TimeKeep",
        description="TimeKeep API",
        version="1.0",
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
