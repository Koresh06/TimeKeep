from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


from src.core.config import settings



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


# class Database:
#     def __init__(self, db_url: str) -> None:
#         self.db_url = db_url
#         self._engine: AsyncEngine | None = create_async_engine(url=db_url, echo=True)
#         self._sessionmaker: async_sessionmaker[AsyncSession] | None = (
#             async_sessionmaker(
#                 autocommit=False,
#                 autoflush=False,
#                 bind=self._engine,
#             )
#         )

#     async def close(self) -> None:
#         if self._engine is None:
#             raise DatabaseError(message="DatabaseSessionManager is not initialized")
#         await self._engine.dispose()

#         self._engine = None
#         self._sessionmaker = None

#     @contextlib.asynccontextmanager
#     async def session(self) -> AsyncIterator[AsyncSession]:
#         if self._sessionmaker is None:
#             raise DatabaseError(message="DatabaseSessionManager is not initialized")

#         session = self._sessionmaker()
#         try:
#             yield session
#         except Exception as err:
#             await session.rollback()
#             raise DatabaseError(
#                 message=f"An error occurred during the session {err}"
#             ) from err
#         finally:
#             await session.close()