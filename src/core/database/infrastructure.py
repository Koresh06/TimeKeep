from typing import AsyncGenerator
from sqlalchemy import AsyncAdaptedQueuePool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.intarface import IDatabase
from src.core.config import settings


class PostgresSQLDatabaseHelper(IDatabase):
    def __init__(self):
        self.engine = self.get_engine()
        self.sessionmaker = self.get_sessionmaker()

    def get_engine(self) -> AsyncEngine:
        return create_async_engine(
            url=settings.db.construct_sqlalchemy_url(),
            query_cache_size=1200,
            poolclass=AsyncAdaptedQueuePool,
            pool_recycle=1800, 
            pool_pre_ping=True, 
            future=True,
            echo=False,
        )

    def get_sessionmaker(self) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            autoflush=False
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.sessionmaker() as session:
            yield session


db_helper = PostgresSQLDatabaseHelper()