from datetime import datetime, timedelta
from typing import Annotated
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from src.models import User
from src.core.database.infrastructure import db_helper
from src.core.config import settings
from src.api.v1.auth.dependencies import get_current_user
from src.api.conf_static import templates
from src.api.v1.auth.schemas import Token, LoginForm
from src.api.v1.auth.service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.get("/", response_class=HTMLResponse)
async def authentication_page(
    request: Request,
):
    if "access_token" in request.cookies:
        redirect_response = RedirectResponse(url="/auth/", status_code=status.HTTP_302_FOUND)
        redirect_response.delete_cookie(key="access_token", httponly=True)
        return redirect_response
    else:
        return templates.TemplateResponse(request=request, name="auth.html")



@router.post(
    "/access-token",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    description="Get access token",
    name="auth:access_token",
)
async def login_access_token(
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
    session: Annotated[
        AsyncSession,
        Depends(db_helper.get_session),
    ],
) -> Token:
    return await AuthService(session).authenticate_and_create_token(form_data)


@router.post(
    "/",
    response_class=RedirectResponse,
    status_code=status.HTTP_200_OK,
    description="Login and get token",
    name="auth:login",
)
async def login(
    request: Request,
    form_data: Annotated[LoginForm, Depends(LoginForm.as_form)],
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
):
    try:
        oauth_form_data = OAuth2PasswordRequestForm(
            username=form_data.username,
            password=form_data.password,
            scope="",
        )

        # Получаем токен через сервис
        token = await AuthService(session).authenticate_and_create_token(
            oauth_form_data
        )

        response = RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)

        # Устанавливаем токен в cookie
        response.set_cookie(
            key="access_token",
            value=token.access_token,
            max_age=settings.api.access_token_expire_minutes * 60, 
            httponly=True,
        )

        return response

    except HTTPException as e:
        # Перехватываем исключение и передаем сообщение об ошибке на фронт
        return templates.TemplateResponse(
            "auth.html", {"request": request, "msg": e.detail}
        )


@router.get(
    path="/logout",
    status_code=status.HTTP_200_OK,
    description="Logout user by clearing the access token and redirecting to auth page",
)
async def logout(
    current_user: User = Depends(get_current_user),
):
    redirect_response = RedirectResponse(url="/auth/", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token", httponly=True)
    
    return redirect_response