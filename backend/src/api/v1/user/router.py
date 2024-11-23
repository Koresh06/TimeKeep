from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession


from models.user import Role, User
from core.session import get_async_session
from .service import UserService
from .schemas import UserOut, UserCreate

router = APIRouter(
    prefix="/user",
    tags=["user"],
)


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_create: UserCreate,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    user = await UserService(session).create_user(data=user_create)
    return user
