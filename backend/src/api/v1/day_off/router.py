from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.session import get_async_session
from models import User, Role

from .schemas import DayOffOut, DayOffCreate
from .service import DayOffService
from api.v1.auth.dependencies import get_current_user
from api.v1.auth.permissions import RoleRequired



router = APIRouter(
    prefix="/day_off",
    tags=["day_off"],
)


@router.post(
    "/",
    response_model=DayOffOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR, Role.USER]))],
    name="day_off:create",
    description="Create day_off",
)
async def create_day_off(
    session: Annotated[
        AsyncSession,
        Depends(get_async_session),
    ],
    day_off_create: DayOffCreate,
    current_user: User = Depends(get_current_user),
):
    return await DayOffService(session).create(
        current_user=current_user,
        day_off_create=day_off_create,
    )
