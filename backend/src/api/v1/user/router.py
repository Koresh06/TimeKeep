from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.session import get_db
from .schemas import UserCreateSchema, UserResponseSchema
from .service import UserService


router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    path="/registration",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
    description="User registration.",
)
async def admin_registration(
    session: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
    user_create: UserCreateSchema = Depends(UserCreateSchema.as_form),
):
    """User registration."""
    user = await UserService(session).registration(user_create=user_create)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not created"
        )
    return user
