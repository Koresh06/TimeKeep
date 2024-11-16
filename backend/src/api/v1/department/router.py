from typing import Annotated, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.session import get_async_session
from models import Department
from .schemas import DepartmentOut, DepartmentCreate, DepartmentUpdatePartil
from .service import DepartmentService
from .dependencies import department_by_id
from ..auth.users import current_superuser


router = APIRouter(
    prefix="/department",
    tags=["department"],
)


@router.post(
    "/",
    response_model=DepartmentOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(current_superuser)],
)
async def create_department(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    department_create: DepartmentCreate,
):
    """Создание отдела"""
    return await DepartmentService(session).create(department_create=department_create)


@router.get(
    "/",
    response_model=List[DepartmentOut],
    status_code=status.HTTP_200_OK,
)
async def get_all_departments(
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Получить все отделы"""
    return await DepartmentService(session).get_all()


@router.get(
    "/{id}",
    response_model=DepartmentOut,
    status_code=status.HTTP_200_OK,
)
async def get_one_department(department: Department = Depends(department_by_id)):
    """Получить отдел по идентификатору"""
    return department


@router.patch(
    "/{id}",
    response_model=DepartmentOut,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(current_superuser)],
)
async def modify_department(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    department_update: DepartmentUpdatePartil,
    department: Department = Depends(department_by_id),
):
    print(department)
    """Модификация отдел по идентификатору"""
    return await DepartmentService(session).modify(
        department=department,
        department_update=department_update,
        partil=True,
    )


@router.put(
    "/{id}",
    response_model=DepartmentOut,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(current_superuser)],
)
async def replace_department(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    department_update: DepartmentUpdatePartil,
    department: Department = Depends(department_by_id),
):
    """Замена отдела по идентификатору"""
    return await DepartmentService(session).replace(
        department=department,
        department_update=department_update,
    )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(current_superuser)],
)
async def delete_department(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    department: Department = Depends(department_by_id),
):
    """Удаление отдела по идентификатору"""
    await DepartmentService(session).delete(department=department)
