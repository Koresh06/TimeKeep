from fastapi import APIRouter, status, Depends, HTTPException, Query
from typing import Annotated, List
from sqlalchemy.ext.asyncio import AsyncSession

from core.session import get_async_session
from .service import OvertimeService
from models import Overtime
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
async def create_overtime(
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
async def get_all_overtimes(
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
async def get_one_overtime(
    overtime: OvertimeOut = Depends(overtime_by_oid),
):
    return overtime


@router.patch(
    "/{oid}",
    response_model=OvertimeOut,
    status_code=status.HTTP_200_OK,
    name="overtime:modify",
    description="Modify overtime",
)
async def modify_overtime(
    session: Annotated[
        AsyncSession,
        Depends(get_async_session),
    ],
    overtime_update: OvertimeUpdatePartial,
    overtime: Overtime = Depends(overtime_by_oid),
):
    return await OvertimeService(session).modify(
        overtime=overtime,
        overtime_update=overtime_update,
        partial=True,
    )


@router.put(
    "/{oid}",
    response_model=OvertimeOut,
    status_code=status.HTTP_200_OK,
    name="overtime:replace",
    description="Replace overtime",
)
async def replace_overtime(
    session: Annotated[
        AsyncSession,
        Depends(get_async_session),
    ],
    overtime_update: OvertimeUpdate,
    overtime: Overtime = Depends(overtime_by_oid),
):
    return await OvertimeService(session).replace(
        overtime=overtime,
        overtime_update=overtime_update,
)


@router.delete(
    "/{oid}",
    status_code=status.HTTP_204_NO_CONTENT,
    name="overtime:delete",
    description="Delete overtime",
)
async def delete_overtime(
    session: Annotated[
        AsyncSession,
        Depends(get_async_session),
    ],
    overtime: Overtime = Depends(overtime_by_oid),
):
    await OvertimeService(session).delete(overtime=overtime)