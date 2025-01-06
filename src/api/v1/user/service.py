from typing import List, Optional
import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User, Role
from .repository import UserRepository
from .schemas import (
    UserOut,
    UserCreate,
    UserFilterParams,
    UserUpdatePartial,
    UserUpdate,
)


class UserService:

    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session=session)

    async def get_user(self, username: str) -> UserOut:
        user = await self.repository.get_user_by_username(username=username)
        if not user:
            return None
        return user
    

    async def get_user_by_id(self, oid: uuid.UUID) -> Optional[User]:
        return await self.repository.get_user_by_id(oid=oid)


    async def create(self, data: UserCreate) -> UserOut:
        user = await self.get_user(username=data.username)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь с таким именем уже существует"
            )
        user = await self.repository.create(data=data)
        return UserOut.model_validate(user)
    

    async def create_superuser(self, data: UserCreate):
        user = await self.repository.create(data=data)
        return user


    async def get_all(
        self,
        filters_params: UserFilterParams,
    ) -> List[UserOut]:
        users = await self.repository.get_all(filters_params=filters_params)
        return [UserOut.model_validate(user) for user in users]


    async def get_one(self, oid: uuid.UUID) -> UserOut:
        user = await self.repository.get_one(oid=oid)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {oid} not found!",
            )
        return UserOut.model_validate(user)


    async def modify(
        self,
        user: UserOut,
        user_update: UserUpdatePartial,
        partil: bool = False,
    ) -> UserOut:
        user = await self.repository.update(
            user=user,
            user_update=user_update,
            partil=partil,
        )
        return UserOut.model_validate(user)
    

    async def replace(
        self,
        user: UserOut,
        user_update: UserUpdate,
        partil: bool = False,
    ) -> UserOut:
        user = await self.repository.update(
            user=user,
            user_update=user_update,
            partil=partil,
        )
        return UserOut.model_validate(user)


    async def delete(self, user: UserOut):
        await self.repository.delete(user=user)


    async def toggle_role(self, user: UserOut, role: Role):
        user = await self.repository.toggle_role(user=user, role=role)
        return UserOut.model_validate(user)