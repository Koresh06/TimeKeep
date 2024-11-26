from datetime import datetime
from typing import Annotated, List, Optional
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import Role, User
from core.session import get_async_session
from api.v1.auth.dependencies import get_current_user
from .service import UserService
from .schemas import (
    UserOut,
    UserCreate,
    UserFilterParams,
    UserUpdatePartial,
    UserUpdate,
)
from .dependencies import get_current_superuser, user_by_oid

router = APIRouter(
    prefix="/user",
    tags=["user"],
)


@router.post(
    "/register",
    response_model=UserOut,
    dependencies=[Depends(get_current_superuser)],
    status_code=status.HTTP_201_CREATED,
    name="users:register",
    description="Create user",
)
async def register(
    user_create: UserCreate,
    session: Annotated[
        AsyncSession,
        Depends(get_async_session),
    ],
):
    user = await UserService(session).create_user(data=user_create)
    return user


@router.get(
    "/",
    response_model=List[UserOut],
    # dependencies=[Depends(get_current_superuser)],
    status_code=status.HTTP_200_OK,
    name="users:get_all",
    description="Get all users with filters and pagination",
)
async def get_all(
    session: Annotated[
        AsyncSession,
        Depends(get_async_session),
    ],
    filters_params: UserFilterParams = Depends(),
):
    return await UserService(session).get_all(filters_params=filters_params)


@router.get(
    "/me",
    response_model=UserOut,
    dependencies=[Depends(get_current_user)],
    status_code=status.HTTP_200_OK,
    name="users:me",
    description="Get current user",
)
async def get_me(
    user: Annotated[
        User,
        Depends(get_current_user),
    ]
):
    return UserOut.model_validate(user)


@router.get(
    "/{oid}",
    response_model=UserOut,
    dependencies=[Depends(get_current_superuser)],
    status_code=status.HTTP_200_OK,
    name="users:get_one",
    description="Get one user by id",
)
async def get_one(
    user: UserOut = Depends(user_by_oid),
):
    return user


@router.patch(
    "/{oid}",
    response_model=UserOut,
    # dependencies=[Depends(get_current_superuser)],
    status_code=status.HTTP_200_OK,
    name="users:modify",
    description="Modify user by id",
)
async def modify(
    session: Annotated[
        AsyncSession,
        Depends(get_async_session),
    ],
    user_update: UserUpdatePartial,
    user: User = Depends(user_by_oid),
):
    return await UserService(session).modify(
        user=user,
        user_update=user_update,
        partil=True,
    )
