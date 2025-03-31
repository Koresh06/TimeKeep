import logging
from fastapi import FastAPI, Request, HTTPException, status
from sqlalchemy.exc import DatabaseError, IntegrityError
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.api.conf_static import templates


logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("errors.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def register_error_handlers(app: FastAPI) -> None:

    @app.exception_handler(ValidationError)
    def handle_pydantic_validation_error(request: Request, exc: ValidationError):
        logger.error(f"Ошибка валидации: {exc.errors()}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": "Ошибка валидации данных. Проверьте введённые данные и попробуйте снова.",
                "details": exc.errors(),
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    @app.exception_handler(DatabaseError)
    def handle_database_error(request: Request, exc: DatabaseError):
        logger.error(f"Ошибка базы данных: {exc}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": "Ошибка базы данных. Попробуйте позже или обратитесь к администратору.",
                "details": str(exc),
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    @app.exception_handler(IntegrityError)
    def handle_integrity_error(request: Request, exc: IntegrityError):
        logger.error(f"Ошибка целостности данных: {exc}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": "Ошибка целостности данных. Возможно, вы пытаетесь добавить дубликат.",
                "details": str(exc),
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    @app.exception_handler(StarletteHTTPException)
    def handle_http_exception(request: Request, exc: StarletteHTTPException):
        error_messages = {
            status.HTTP_404_NOT_FOUND: "Страница не найдена. Проверьте адрес и попробуйте снова.",
            status.HTTP_403_FORBIDDEN: "Доступ запрещён. У вас недостаточно прав для выполнения этой операции.",
            status.HTTP_401_UNAUTHORIZED: "Требуется авторизация. Войдите в систему и попробуйте снова.",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Внутренняя ошибка сервера. Попробуйте позже.",
        }
        logger.error(f"HTTP ошибка {exc.status_code}: {exc.detail}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": error_messages.get(exc.status_code, "Произошла неизвестная ошибка."),
                "details": str(exc.detail),
            },
            status_code=exc.status_code
        )
