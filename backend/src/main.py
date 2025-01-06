import sys
sys.dont_write_bytecode = True

import uvicorn
import logging
import betterlogging as bl

from fastapi import FastAPI
from api.v1.router_registration import register_routers
from core.config import settings


logger = logging.getLogger("my_app")


def setup_logging() -> None:
    """
    Set up logging configuration for the application.

    This method initializes the logging configuration for the application.
    """
    log_level = logging.INFO
    
    bl.basic_colorized_config(level=log_level)

    file_handler = logging.FileHandler("app.log")
    file_handler.setLevel(log_level)
    formatter = logging.Formatter(
        "%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.setLevel(log_level)

    logger.info("Логирование настроено и приложение запускается...")


app = FastAPI(
    title="TimeKeep",
    description="TimeKeep API",
    version="1.0",
)


register_routers(app)


@app.get("/")
def read_root() -> dict:
    """Read root."""
    logger.info("Обработан запрос к корневому маршруту")
    return {"Hello": "World"}


if __name__ == "__main__":
    try:
        setup_logging()

        uvicorn.run(
            app=app,
            host=settings.api.host, # type: ignore
            port=settings.api.port, # type: ignore
        )

    except KeyboardInterrupt:
        logger.info("Программа завершена пользователем")
