import pdb
from typing import Annotated, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.session import get_async_session
from models import Department, Role
from api.v1.auth.permissions import RoleRequired
from .schemas import DepartmentOut, DepartmentCreate, DepartmentUpdatePartil
from .service import DepartmentService
from .dependencies import department_by_oid


router = APIRouter(
    prefix="/department",
    tags=["department"],
)


@router.post(
    "/",
    response_model=DepartmentOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(RoleRequired(Role.SUPERUSER)),
    ],
    name="department:create",
    description="Create department",
)
async def create_department(
    session: Annotated[
        AsyncSession,
        Depends(get_async_session),
    ],
    department_create: DepartmentCreate,
):
    return await DepartmentService(session).create(department_create=department_create)


@router.get(
    "/",
    response_model=List[DepartmentOut],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR, Role.USER]))],
    name="department:get_all",
    description="Get all departments",
)
async def get_all_departments(
    session: Annotated[
        AsyncSession,
        Depends(get_async_session),
    ],
):
    return await DepartmentService(session).get_all()


@router.get(
    "/{oid}",
    response_model=DepartmentOut,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR]))],
    name="department:get_one",
    description="Get one department by id",
)
async def get_one_department(department: Department = Depends(department_by_oid)):
    return department


@router.patch(
    "/{oid}",
    response_model=DepartmentOut,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleRequired(Role.SUPERUSER))],
    name="department:modify",
    description="Modify department by id",
)
async def modify_department(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    department_update: DepartmentUpdatePartil,
    department: Department = Depends(department_by_oid),
):
    return await DepartmentService(session).modify(
        department=department,
        department_update=department_update,
        partil=True,
    )


@router.put(
    "/{oid}",
    response_model=DepartmentOut,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleRequired(Role.SUPERUSER))],
    name="department:replace",
    description="Replace department by id",
)
async def replace_department(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    department_update: DepartmentUpdatePartil,
    department: Department = Depends(department_by_oid),
):
    return await DepartmentService(session).replace(
        department=department,
        department_update=department_update,
    )


@router.delete(
    "/{oid}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RoleRequired(Role.SUPERUSER))],
    name="department:delete",
    description="Delete department by id",
)
async def delete_department(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    department: Department = Depends(department_by_oid),
):
    await DepartmentService(session).delete(department=department)
