from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.config import settings

from models import User


engine = create_async_engine(
    url=settings.db.construct_sqlalchemy_url(),
    query_cache_size=1200,
    pool_size=20,
    max_overflow=200,
    future=True,
    echo=False,
)


async_session_maker = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        except:
            await session.rollback()
            raise
        finally:
            await session.close()
