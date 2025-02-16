from typing import Annotated, List
from urllib.parse import quote, unquote
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.auth.dependencies import get_current_user
from src.api.v1.day_off.dependencies import count_notifications_day_offs
from src.core.session import get_async_session
from src.middlewares.notification.dependencies import get_unread_notifications_count_user
from src.models import Department, Role
from src.api.v1.auth.permissions import RoleRequired
from src.api.v1.department.schemas import DepartmentOut, DepartmentCreate, DepartmentUpdatePartil
from src.api.v1.department.service import DepartmentService
from src.api.v1.organization.service import OrganizationService
from src.api.v1.department.dependencies import department_by_oid
from src.api.conf_static import templates
from src.models.user import User


router = APIRouter(
    prefix="/department",
    tags=["department"],
)



@router.get(
    "/create",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER]))],
    name="department:create",
    description="Create department",
)
async def create_department_page(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: User = Depends(get_current_user),
    count_day_offs: int = Depends(count_notifications_day_offs),
    notifications_count_user: int = Depends(get_unread_notifications_count_user),
):
    organizations = await OrganizationService(session).get_all_dep_organizations()

    success_message = request.cookies.get("success_message")
    if success_message:
        success_message = unquote(success_message)

    response = templates.TemplateResponse(
        request=request,
        name="departments/create.html",
        context={
            "msg": success_message,
            "current_user": current_user,
            "count_day_offs": count_day_offs,
            "notifications_count_user": notifications_count_user,
            "organizations": organizations,
        },
    )

    if success_message:
        response.delete_cookie("success_message")
    return response


@router.post(
    "/create",
    response_model=DepartmentOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleRequired(Role.SUPERUSER))],
    name="department:create",
    description="Create department",
)
async def create_department(
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(get_async_session),
    ],
    current_user: User = Depends(get_current_user),
    department_create: DepartmentCreate = Depends(DepartmentCreate.as_form),
):
    try:
        await DepartmentService(session).create(
            department_create=department_create,
        )
        response = RedirectResponse(
            url="/department/create",
            status_code=status.HTTP_303_SEE_OTHER,
        )
        success_message = quote("✔️ Департамент успешно создана!")
        response.set_cookie(key="success_message", value=success_message)
        return response
    
    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="departments/create.html",
            context={
                "error": str(e),
                "current_user": current_user,
            },
        )




@router.get(
    "/edit/{oid}",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER]))],
    name="department:modify",
    description="Modify department",
)
async def edit_department_page(
    request: Request,
    department: Department = Depends(department_by_oid),
    current_user: User = Depends(get_current_user),
    count_day_offs: int = Depends(count_notifications_day_offs),
    notifications_count_user: int = Depends(get_unread_notifications_count_user),
):
    return templates.TemplateResponse(
        request=request,
        name="departments/edit.html",
        context={
            "current_user": current_user,
            "department": department,
            "count_day_offs": count_day_offs,
            "notifications_count_user": notifications_count_user
        },
    )


@router.post(
    "/edit/{oid}",
    response_class=RedirectResponse,
    status_code=status.HTTP_302_FOUND,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER]))],
    name="department:modify",
    description="Modify department",
)
async def modify_department(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    department: Department = Depends(department_by_oid),
    department_update: DepartmentUpdatePartil = Depends(DepartmentUpdatePartil.as_form),
):
    await DepartmentService(session).modify(
        department=department,
        department_update=department_update,
        partil=True,
    )
    return RedirectResponse(url=f"/organization/", status_code=status.HTTP_302_FOUND)




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
