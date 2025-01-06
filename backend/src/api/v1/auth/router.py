from typing import Annotated
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Request, Response, status

from models import User
from core.session import get_async_session
from core.config import settings

from api.v1.auth.dependencies import get_current_user
from api.conf_static import templates
from .schemas import Token, LoginForm
from .service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.get("/", response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth.html",
    )


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
        Depends(get_async_session),
    ],
) -> Token:
    return await AuthService(session).authenticate_and_create_token(form_data)


@router.post(
    "/login",
    response_class=RedirectResponse,
    status_code=status.HTTP_200_OK,
    description="Login and get token",
    name="auth:login",
)
async def login(
    response: Response,
    form_data: Annotated[
        LoginForm,
        Depends(LoginForm.as_form),
    ],
    session: Annotated[
        AsyncSession,
        Depends(get_async_session),
    ],
):
    oauth_form_data = OAuth2PasswordRequestForm(
        username=form_data.username,
        password=form_data.password,
        scope="",
    )
    token = await AuthService(session).authenticate_and_create_token(oauth_form_data)

    response.set_cookie(
        key="access_token",
        value=token.access_token,
        max_age=settings.api.access_token_expire_minutes * 60,  # type: ignore
        httponly=True,
        secure=True,
        samesite="strict",
    )

    return RedirectResponse(url='/overtimes/', status_code=status.HTTP_302_FOUND)


@router.post(
    path="/logout",
    status_code=status.HTTP_200_OK,
    description="Logout user by clearing the access token",
)
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
):
    response.delete_cookie(key="access_token")

    return JSONResponse(
        content={"message": "Successfully logged out"},
        status_code=status.HTTP_200_OK,
    )
