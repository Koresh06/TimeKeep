import uvicorn
import logging
import betterlogging as bl

from fastapi import FastAPI

from core.config import settings


logger = logging.getLogger(__name__)


def setup_logging():
    """
    Set up logging configuration for the application.

    This method initializes the logging configuration for the application.
    It sets the log level to INFO and configures a basic colorized log for
    output. The log format includes the filename, line number, log level,
    timestamp, logger name, and log message.

    Returns:
        None

    Example usage:
        setup_logging()
    """
    log_level = logging.INFO
    bl.basic_colorized_config(level=log_level)

    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")


app = FastAPI()


@app.get("/")
def read_root() -> dict:
    """Read root."""
    return {"Hello": "World"}


if __name__ == "__main__":
    setup_logging()

    uvicorn.run(
        app=app,
        host=settings.api.host,
        port=settings.api.port,
    )
