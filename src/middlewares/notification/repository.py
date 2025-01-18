from sqlalchemy.future import select
from sqlalchemy import func, Result

from src.core.repo.base import BaseRepo
from src.models.user import User

class NotificationRepository(BaseRepo):

    async def get_inactive_users_count(self) -> int:
        stmt = select(func.count(User.oid)).filter(
            User.is_active == False
        )
        result: Result = await self.session.scalar(stmt)
        return result
