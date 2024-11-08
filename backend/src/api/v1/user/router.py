import logging

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.session import get_db
from models import User
from .schemas import UserCreateSchema, UserResponseSchema
from .service import UserService
from ..auth.permissions import get_current_user  



router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    path="/registration",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
    description="Registration user",
)
async def admin_registration(
    session: Annotated[AsyncSession, Depends(get_db)],
    user_create: UserCreateSchema = Depends(UserCreateSchema.as_form),
) -> UserResponseSchema:
    user = await UserService(session).registration(user_create=user_create)
    
    if not user:
        logging.warning("User not created: no user returned by service")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not created"
        )
    
    logging.info(f"User created: {user.oid}")
    return user


@router.get(
    path="/me",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
    description="Get current user info",
)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponseSchema:
    logging.info(f"Retrieving information for user: {current_user.oid}")
    return current_user


