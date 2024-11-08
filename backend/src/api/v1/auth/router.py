from typing import Annotated
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Request, Response, status

from models import User
from api.v1.auth.jwt import create_token
from core.session import get_db
from core.config import settings

from .schemas import LoginForm, LoginResponse, Token
from .service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    path="/access-token",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    description="Авторизация пользователя",
)
async def login_access_token(
    response: Response,
    from_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
    session: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
):
    """Авторизация пользователя"""
    user: User = await AuthService(session).authenticate(
        email=from_data.username,
        password=from_data.password,
    )

    if not user:
        return None

    token = create_token(user_oid=user.oid)

    return token


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
):
    # Создание формы
    form = LoginForm(request=request)
    await form.create_oauth_form()

    # Проверка и получение токена
    validate_user_cookie = await login_access_token(
        response=Response(),
        from_data=form,
        session=session,
    )
    if validate_user_cookie is None:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Invalid credentials"})

    # Создаем ответ с токеном
    response_data = {
        "access_token": validate_user_cookie["access_token"],
        "token_type": "bearer",  # или что-то другое, зависит от вашей логики
    }

    # Устанавливаем cookie (если требуется) и возвращаем JSON
    response = JSONResponse(content=response_data)
    response.set_cookie(
        key="access_token",
        value=validate_user_cookie["access_token"],
        httponly=True,
        expires=settings.api.access_token_expire_minutes * 60,
    )

    return response

