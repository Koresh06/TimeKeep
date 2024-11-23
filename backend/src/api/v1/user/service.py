from typing import List
import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from models import Department
from .repository import UserRepository
from .schemas import UserOut, UserCreate


class UserService:

    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session=session)

    async def get_user(self, username: str) -> UserOut:
        user = await self.repository.get_user_by_username(username=username)
        if not user:
            return None
        return user

    async def create_user(self, data: UserCreate) -> UserOut:
        user = await self.get_user(username=data.username)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )
        user = await self.repository.create_user(data=data)
        return UserOut.model_validate(user)
        
