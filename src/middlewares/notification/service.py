import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from .repository import NotificationRepository


class NotificationService:

    def __init__(self, session: AsyncSession):
        self.repository = NotificationRepository(session=session)


    async def get_inactive_users_count(self) -> int:
        return await self.repository.get_inactive_users_count()