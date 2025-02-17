from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator


class IDatabase(ABC):
    @abstractmethod
    def get_engine(self) -> AsyncEngine:
        pass

    @abstractmethod
    def get_sessionmaker(self) -> sessionmaker:
        pass

    @abstractmethod
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        pass
