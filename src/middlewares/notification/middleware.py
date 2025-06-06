# middlewares/notification_middleware.py
from typing import Annotated
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.infrastructure import db_helper
from src.middlewares.notification.service import NotificationService


class NotificationMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, 
        request: Request,
        call_next,
    ):
        async with db_helper.sessionmaker() as session:
            notifications_count_user = await NotificationService(session).get_inactive_users_count()

            request.state.notifications_count_user = notifications_count_user
            response = await call_next(request)

            return response
