from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from fastapi import Depends

from core.session import get_async_session
from models import User


class CustomSQLAlchemyUserDatabase(SQLAlchemyUserDatabase):

    async def get_by_username(self, username: str) -> Optional[User]:
        query = await self.session.execute(
            select(User).where(User.username == username)
        )
        return query.scalars().first()


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield CustomSQLAlchemyUserDatabase(session, User)