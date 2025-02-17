from typing import Annotated
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.conf_static import templates
from src.api.v1.day_off.dependencies import count_notifications_day_offs
from src.core.database.infrastructure import db_helper
from src.api.v1.auth.dependencies import get_current_user
from src.middlewares.notification.dependencies import get_unread_notifications_count_user
from src.models import User


router = APIRouter(
    prefix="/home"
)

@router.get("/", response_class=HTMLResponse)
async def home_page(
    request: Request, 
    session: Annotated[
        AsyncSession,
        Depends(db_helper.get_session),
    ],
    current_user: User = Depends(get_current_user),
    count_day_offs: int = Depends(count_notifications_day_offs),
    notifications_count_user: int = Depends(get_unread_notifications_count_user),
):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "current_user": current_user,
            "count_day_offs": count_day_offs,
            "notifications_count_user": notifications_count_user
        },
    )
    