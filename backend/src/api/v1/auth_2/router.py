from typing import Annotated
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from api.v1.auth_2.permissions import get_current_user
from models import User
from api.v1.auth_2.jwt import create_token
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
    path="/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    description="Login and get token",
)
async def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    # Проверяем данные пользователя
    user = await AuthService(session).authenticate(
        username=form_data.username,
        password=form_data.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Создаем токен
    token = create_token(user_oid=user.oid)

    # Устанавливаем токен как cookie (если требуется)
    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,
        max_age=settings.api.access_token_expire_minutes * 60,
    )

    # Возвращаем токен
    return token





