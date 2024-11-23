from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession


from models.user import Role, User
from core.session import get_async_session
from .service import UserService
from .schemas import UserOut, UserCreate
from ..auth.dependencies import get_current_user
from .dependencies import get_current_superuser

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
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    user = await UserService(session).create_user(data=user_create)
    return user


@router.get(
    "/me",
    response_model=UserOut,
    dependencies=[Depends(get_current_user)],
    status_code=status.HTTP_200_OK,
    name="users:me",
    description="Get current user",
)
async def get_me(user: Annotated[User, Depends(get_current_user)]):
    return UserOut.model_validate(user)