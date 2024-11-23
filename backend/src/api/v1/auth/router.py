from typing import Annotated
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Response, status

from models import User
from api.v1.auth.jwt import create_token
from core.session import get_async_session
from core.config import settings

from .schemas import Token
from .dependencies import authenticate_user, get_current_user


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    path="/access-token",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    description="Login and get token",
)
async def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    user = await authenticate_user(
        session=session,
        username=form_data.username,
        password=form_data.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_token(user_oid=user.oid)

    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,
        max_age=settings.api.access_token_expire_minutes * 60,
    )

    return token


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
