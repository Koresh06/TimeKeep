from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.session import get_async_session
from models import Department
from .schemas import DepartmentOut, DepartmentCreate
from .service import DepartmentService
from .dependencies import department_by_id



router = APIRouter(
    prefix="/department",
    tags=["department"]
)


@router.post(
    "/",
    response_model=DepartmentOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_department(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    department_create: DepartmentCreate
):
    """Создание отдела"""
    return await DepartmentService(session).create(department_create=department_create)


@router.get(
    "/{id}",
    response_model=DepartmentOut,
    status_code=status.HTTP_200_OK,
)
async def get_one_department(
    department: Department = Depends(department_by_id)
):
    """Получить отдел по идентификатору"""
    return department

