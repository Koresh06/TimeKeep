from typing import Annotated, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.session import get_async_session
from models import User, Role

from .schemas import DayOffOut, DayOffCreate, DayOffExtendedOut, PaginatedResponse
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


@router.get(
    "/superuser",
    response_model=PaginatedResponse[DayOffExtendedOut],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER]))],
    name="day_off:get_all_superuser",
    description="Get all day offs for superuser",
)
async def get_all_day_offs_superuser(
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
    "/moderator",
    response_model=PaginatedResponse[DayOffExtendedOut],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleRequired([Role.MODERATOR]))],
    name="day_off:get_all_moderator",
    description="Get day offs for moderator within their department",
)
async def get_all_day_offs_moderator(
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
    "/user",
    response_model=PaginatedResponse[DayOffOut],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleRequired([Role.USER]))],
    name="day_off:get_all_user",
    description="Get only user's own day offs",
)
async def get_all_day_offs_user(
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
