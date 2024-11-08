from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.config import settings


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


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        except Exception as e:
            # Обработка исключения (если нужно, например, логирование)
            print(f"Ошибка при работе с сессией: {e}")
            raise  # Перебрасываем исключение, чтобы FastAPI мог его обработать
        finally:
            await session.close()  # Закрываем сессию в любом случае