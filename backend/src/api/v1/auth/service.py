from typing import List
import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from models import Department
from .repository import AuthRepository
from .schemas import (
    UserCreate,
    UserOut,
)


class AuthService():

    def __init__(self, session: AsyncSession):
        self.repository = AuthRepository(session=session)

    async def create_superuser(self, user_create: UserCreate) -> UserOut:
        result = await self.repository.create_superuser(user_create=user_create)
        if result:
            return f"Superuser created successfully.\nUsername: {user_create.username}"