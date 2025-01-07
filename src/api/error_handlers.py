from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi import status

async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Обработчик для HTTPException с учётом разных статусов.
    """
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        # Неавторизован - перенаправляем на страницу авторизации
        return RedirectResponse("/auth/", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    
    elif exc.status_code == status.HTTP_403_FORBIDDEN:
        # Доступ запрещён - перенаправляем на страницу ошибки доступа
        return RedirectResponse("/forbidden/", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    
    elif exc.status_code == status.HTTP_404_NOT_FOUND:
        # Не найдено - перенаправляем на страницу "Не найдено"
        return RedirectResponse("/not-found/", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    
    elif exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
        # Внутренняя ошибка сервера - кастомная страница
        return RedirectResponse("/server-error/", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    
    # Для других ошибок возвращаем стандартное исключение
    return exc
