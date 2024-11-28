from fastapi import APIRouter, status, Depends, HTTPException, Query
from typing import Annotated, List
from sqlalchemy.ext.asyncio import AsyncSession

from core.session import get_async_session
from .service import OvertimeService
from .schemas import (
    OvertimeOut,
    OvertimeCreate,
    OvertimeUpdate,
    OvertimeUpdatePartial,
    PaginatedResponse,
)
from .dependencies import overtime_by_oid


router = APIRouter(
    prefix="/overtime",
    tags=["overtime"],
)



@router.post(
    "/",
    response_model=OvertimeOut,
    status_code=status.HTTP_201_CREATED,
    name="overtime:create",
    description="Create overtime",
)
async def create(
    session: Annotated[
        AsyncSession,
        Depends(get_async_session),
    ],
    overtime_create: OvertimeCreate,
):
    return await OvertimeService(session).create(overtime_create=overtime_create)


@router.get(
    "/",
    response_model=PaginatedResponse[OvertimeOut],
    status_code=status.HTTP_200_OK,
    name="overtime:get_all",
    description="Get all overtimes",
)
async def get_all(
    session: Annotated[
        AsyncSession,
        Depends(get_async_session),
    ],
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return await OvertimeService(session).get_all(limit=limit, offset=offset)


@router.get(
    "/{oid}",
    response_model=OvertimeOut,
    status_code=status.HTTP_200_OK,
    name="overtime:get_one",
    description="Get one overtime by id",
)
async def get_one(
    overtime: OvertimeOut = Depends(overtime_by_oid),
):
    return overtime
