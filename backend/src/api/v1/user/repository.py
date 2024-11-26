from datetime import datetime
import uuid

from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy import and_, func, select, Result
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from core.repo.base import BaseRepo
from models import User
from .schemas import UserCreate, UserFilterParams, UserUpdatePartial, UserUpdate
from ..auth.security import get_password_hash


class UserRepository(BaseRepo):

    async def get_user_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        result: Result = await self.session.scalar(stmt)
        return result
    
    async def get_user_by_id(self, oid: uuid.UUID) -> Optional[User]:
        stmt = select(User).where(User.oid == oid)
        result: Result = await self.session.scalar(stmt)
        return result


    async def create(self, data: UserCreate) -> User:
        try:
            hashed_password = get_password_hash(data.password)

            user_data = data.model_dump(exclude={"password"})
            user_data["hashed_password"] = hashed_password
            user = User(**user_data)

            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except IntegrityError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        


    async def get_all(
        self,
        filters_params: UserFilterParams,
    ) -> List[User]:
        filters = []
        try:
            if filters_params.is_active is not None:
                filters.append(User.is_active == filters_params.is_active)
            if filters_params.start_date is not None:
                filters.append(User.create_at >= filters_params.start_date)
            if filters_params.end_date is not None:
                filters.append(User.create_at <= filters_params.end_date)

            query = (
                select(User)
                .where(and_(*filters))
                .offset((filters_params.page - 1) * filters_params.limit)
                .limit(filters_params.limit)
                .order_by(User.create_at.desc())
            )

            result = await self.session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    async def count_all(self, filters: List) -> int:
        query = select(func.count(User.oid)).where(and_(*filters))
        result = await self.session.execute(query)
        return result.scalar()

    async def get_one(self, oid: uuid.UUID) -> User:
        try:
            stmt = select(User).where(User.oid == oid)
            result: Result = await self.session.scalar(stmt)
            return result
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    async def update(
        self,
        user: User,
        user_update: UserUpdate | UserUpdatePartial,
        partil: bool = False,
    ) -> User:
        # try:
        for key, value in user_update.model_dump(exclude_unset=partil).items():
            setattr(user, key, value)
        await self.session.commit()
        await self.session.refresh(user)
        return user
        # except SQLAlchemyError as e:
        #     await self.session.rollback()
        #     raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
