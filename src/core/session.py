from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import AsyncAdaptedQueuePool
from src.core.config import settings

engine = create_async_engine(
    url=settings.db.construct_sqlalchemy_url(),
    query_cache_size=1200,
    poolclass=AsyncAdaptedQueuePool,
    pool_recycle=1800, 
    pool_pre_ping=True, 
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
