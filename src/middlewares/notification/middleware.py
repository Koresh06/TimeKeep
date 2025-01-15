# middlewares/notification_middleware.py
from typing import Annotated
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.session import async_session_maker
from .service import NotificationService


class NotificationMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, 
        request: Request,
        call_next,
    ):
        async with async_session_maker() as session:
            notifications_count = await NotificationService(session).get_inactive_users_count()

            request.state.notifications_count = notifications_count
            response = await call_next(request)

            return response
