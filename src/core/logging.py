import logging
import betterlogging as bl

def setup_logging() -> None:
    """
    Set up logging configuration for the application.

    This method initializes the logging configuration for the application.
    """
    log_level = logging.INFO

    # Настройка цветного вывода в консоль
    bl.basic_colorized_config(level=log_level)

    # Логирование в файл
    file_handler = logging.FileHandler("app.log")
    file_handler.setLevel(log_level)
    formatter = logging.Formatter(
        "%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    logger = logging.getLogger("my_app")
    logger.addHandler(file_handler)
    logger.setLevel(log_level)

    logger.info("Логирование настроено и приложение запускается...")
