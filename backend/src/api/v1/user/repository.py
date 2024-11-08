import uuid

from typing import List, Optional
from sqlalchemy.future import select

from models import User
from api.v1.auth.security import get_password_hash
from core.repo.base import BaseRepo
from api.v1.user.schemas import UserCreateSchema, UserUpdateSchema


class UserRepository(BaseRepo):

    async def get_user_by_id(self, user_oid: uuid.UUID) -> Optional[User]:
        stmt = select(User).where(User.oid == user_oid)
        result = await self.session.scalar(stmt)
        return result


    async def get_users(self, skip: int = 0, limit: int = 10) -> List[User]:
        stmt = select(User).offset(skip).limit(limit)
        result = await self.session.scalars(stmt)
        return result


    async def create_user(self, user_create: UserCreateSchema) -> User:
        _hashed_password = get_password_hash(user_create.password)
        user = User(
            oid=user_create.oid,
            department_oid=user_create.department_oid,
            username=user_create.username,
            _hashed_password=_hashed_password,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user


    async def update_user(self, user_oid: uuid.UUID, user_update: UserUpdateSchema) -> Optional[User]:
        stmt = select(User).where(User.oid == user_oid)
        user = await self.session.scalar(stmt)
        if user:
            for key, value in user_update.model_dump(exclude_unset=True).items():
                setattr(user, key, value)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        return None


    async def delete_user(self, user_oid: int) -> Optional[User]:
        stmt = select(User).where(User.oid == user_oid)
        user = await self.session.scalar(stmt)
        if user:
            await self.session.delete(user)
            await self.session.commit()
            return user
        return None