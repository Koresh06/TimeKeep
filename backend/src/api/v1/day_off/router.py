from typing import Annotated, List
import uuid
from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.session import get_async_session
from models import User, Role, DayOff

from .schemas import (
    DayOffOut,
    DayOffCreate,
    DayOffExtendedOut,
    PaginatedResponse,
    DayOffUpdate,
    DayOffUpdatePartil,
)
from .service import DayOffService
from api.v1.auth.dependencies import get_current_user
from api.v1.auth.permissions import RoleRequired
from .dependencies import day_off_by_oid


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


@router.get(
    "/",
    response_model=PaginatedResponse[DayOffOut | DayOffExtendedOut],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR, Role.USER]))],
    name="day_off:get_all",
    description="Get all day offs",
)
async def get_all_day_offs(
    session: Annotated[
        AsyncSession,
        Depends(get_async_session),
    ],
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return await DayOffService(session).get_all(
        current_user=current_user,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{oid}",
    response_model=DayOffOut | DayOffExtendedOut,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR, Role.USER]))],
    name="day_off:get_one",
    description="Get one day off by id",
)
async def get_one_day_off(
    oid: Annotated[uuid.UUID, Path],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: User = Depends(get_current_user),
):
    return await DayOffService(session).get_one(current_user=current_user, oid=oid)


@router.patch(
    "/{oid}",
    response_model=DayOffOut,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR]))],
    name="day_off:modify",
    description="Modify day off by id",
)
async def modify_day_off(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    day_off_update: DayOffUpdatePartil,
    day_off: DayOff = Depends(day_off_by_oid),
):
    return await DayOffService(session).modify(
        day_off=day_off,
        day_off_update=day_off_update,
        partil=True,
    )


@router.delete(
    "/{oid}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR, Role.USER]))],
    name="day_off:delete",
    description="Delete day off by id",
)
async def delete_day_off(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    day_off: DayOff = Depends(day_off_by_oid),
):
    return await DayOffService(session).delete(day_off=day_off)


