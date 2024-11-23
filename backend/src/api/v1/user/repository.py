import uuid

from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy import select, Result
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from core.repo.base import BaseRepo
from models import User
from .schemas import UserCreate
from ..auth.security import get_password_hash


class UserRepository(BaseRepo):

    async def get_user_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        result: Result = await self.session.scalar(stmt)
        return result

    async def create_user(self, data: UserCreate) -> User:
        hashed_password = get_password_hash(data.password)

        user_data = data.model_dump(exclude={"password"})
        user_data["hashed_password"] = hashed_password
        user = User(**user_data)

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user