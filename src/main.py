import sys
sys.dont_write_bytecode = True

import uvicorn
import logging
import betterlogging as bl

from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from api.conf_static import configure_static
from api.v1.router_registration import register_routers
from api.error_handlers import http_exception_handler
from core.config import settings
from core.logging import setup_logging


app = FastAPI(
    title="TimeKeep",
    description="TimeKeep API",
    version="1.0",
)

@app.exception_handler(HTTPException)
async def validation_exception_handler(request: Request, exc: HTTPException):
    return RedirectResponse("/auth/", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

configure_static(app)
register_routers(app)

app.add_exception_handler(HTTPException, http_exception_handler)


@app.get("/")
async def root():
    return RedirectResponse(
        url="/auth/",
        status_code=status.HTTP_302_FOUND,
    )


if __name__ == "__main__":
    try:
        setup_logging()
        uvicorn.run(
            app=app,
            host=settings.api.host,  
            port=settings.api.port,  
        )
    except KeyboardInterrupt:
        print("Программа завершена пользователем")
