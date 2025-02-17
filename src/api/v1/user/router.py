from datetime import datetime
from typing import Annotated, List
from fastapi import APIRouter, Depends, Query, status, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import Role, User
from src.core.database.infrastructure import db_helper
from src.api.conf_static import templates
from src.api.v1.auth.permissions import RoleRequired
from src.api.v1.auth.dependencies import get_current_user
from src.api.v1.department.service import DepartmentService
from src.api.v1.organization.service import OrganizationService
from src.api.v1.user.service import UserService
from src.api.v1.user.schemas import (
    UserOut,
    UserCreate,
    UserFilterParams,
    UserUpdatePartial,
    UserUpdate,
)
from src.api.v1.user.dependencies import user_by_oid
from src.api.v1.day_off.dependencies import count_notifications_day_offs
from src.middlewares.notification.dependencies import get_unread_notifications_count_user


router = APIRouter(
    prefix="/user",
    tags=["user"],
)


@router.get(
    "/register",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    name="users:register",
    description="Register page",
)
async def register_page(
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.get_session),
    ],
):
    organizations = await OrganizationService(session).get_all()
    departments = await DepartmentService(session).get_all()
    
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "organizations": organizations,
            "departments": departments,
        },
    )


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    name="users:register",
    description="Create user",
)
async def register(
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.get_session),
    ],
    user_create: UserCreate = Depends(UserCreate.as_form),
):
    try:
        await UserService(session).create(data=user_create)

        return templates.TemplateResponse(
            request=request,
            name="auth.html",
        )
    except HTTPException as e:
        departments = await DepartmentService(session).get_all()

        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "msg": e.detail,
                "departments": departments,
            },
        )


@router.get(
    "/registration-requests",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    name="users:register_requests",
    description="Register requests page",
)
async def register_requests_page(
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.get_session),
    ],
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    count_day_offs: int = Depends(count_notifications_day_offs),
    notifications_count_user: int = Depends(get_unread_notifications_count_user),
):
    data = await UserService(session).get_all(
        limit=limit,
        offset=offset,
        is_active=False,
    )

    return templates.TemplateResponse(
        request=request,
        name="users/registration_requests.html",
        context={
            "current_user": current_user,
            "count_day_offs": count_day_offs,
            "users": data.items,
            "total_pages": data.total_pages,
            "current_page": data.current_page,
            "limit": limit,
            "offset": offset,
            "count_day_offs": count_day_offs,
            "notifications_count_user": notifications_count_user,
        },
    )


@router.post(
    "/{oid}/approve",
    response_class=RedirectResponse,
    status_code=status.HTTP_200_OK,
    name="user:approve",
    description="Approve or reject user",
)
async def register_requests(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.get_session),
    ],
    user: User = Depends(user_by_oid),
):
    await UserService(session).approve_or_reject_user(
        user=user,
        is_active=True,
    )

    return RedirectResponse(
        url="/user/registration-requests",
        status_code=status.HTTP_302_FOUND,
    )


@router.post(
    "/delete/{oid}",
    dependencies=[Depends(RoleRequired(Role.SUPERUSER))],
    status_code=status.HTTP_204_NO_CONTENT,
    name="user:delete",
    description="Delete user by id",
)
async def delete(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.get_session),
    ],
    user: User = Depends(user_by_oid),
):
    await UserService(session).delete(user=user)

    return RedirectResponse(url="/user/registration-requests", status_code=status.HTTP_303_SEE_OTHER)



@router.get(
    "/me",
    response_class=HTMLResponse,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR, Role.USER]))],
    status_code=status.HTTP_200_OK,
    name="users:me",
    description="Get current user",
)
async def get_me(
    request: Request,
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
    current_user: User = Depends(get_current_user),
    count_day_offs: int = Depends(count_notifications_day_offs),
    notifications_count_user: int = Depends(get_unread_notifications_count_user),
):
    current_year = datetime.now().year

    statistics = await UserService(session).get_statistics_current_user(current_user=current_user, selected_year=current_year)
    return templates.TemplateResponse(
        request=request,
        name="users/profile.html",
        context={
            "current_user": current_user,
            "count_day_offs": count_day_offs,
            "notifications_count_user": notifications_count_user,
            "statistics": statistics,
            "current_year": current_year,
        },
    )

@router.get(
    "/statistics/{year}",
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR, Role.USER]))],
    status_code=status.HTTP_200_OK,
)
async def get_statistics_current_year(
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
    current_user: User = Depends(get_current_user),
    year: int = None,
):
    statistics = await UserService(session).get_statistics_current_user(current_user, selected_year=year)  # Получаем статистику с указанным годом
    return {"statistics": statistics}



@router.get(
    "/",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER]))],
    name="users:get_all",
    description="Get all users",
)
async def get_all(
    request: Request,
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    count_day_offs: int = Depends(count_notifications_day_offs),
    notifications_count_user: int = Depends(get_unread_notifications_count_user),
):
    data = await UserService(session).get_all(
        limit=limit,
        offset=offset,
    )

    return templates.TemplateResponse(
        request=request,
        name="users/get-all.html",
        context={
            "current_user": current_user,
            "users": data.items,
            "total_pages": data.total_pages,
            "current_page": data.current_page,
            "limit": limit,
            "offset": offset,
            "count_day_offs": count_day_offs,
            "notifications_count_user": notifications_count_user,
        },
    )



@router.get(
    "/edit/{oid}",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,    
    dependencies=[Depends(RoleRequired([Role.SUPERUSER]))],
    name="users:edit",
    description="Edit user",
)
async def edit_user_page(
    request: Request,
    user: User = Depends(user_by_oid),
    current_user: User = Depends(get_current_user),
    count_day_offs: int = Depends(count_notifications_day_offs),
    notifications_count_user: int = Depends(get_unread_notifications_count_user),
):
    return templates.TemplateResponse(
        request=request,
        name="users/edit.html",
        context={
            "current_user": current_user,
            "user": user,
            "count_day_offs": count_day_offs,
            "notifications_count_user": notifications_count_user
        },
    )


@router.post(
    "/edit/{oid}",
    response_class=RedirectResponse,
    status_code=status.HTTP_302_FOUND,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER]))],
    name="users:edit",
    description="Edit user",
)
async def edit_user(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.get_session),
    ],
    user: User = Depends(user_by_oid),
    user_update: UserUpdatePartial = Depends(UserUpdatePartial.as_form),
    
):
    await UserService(session).modify(
        user=user,
        user_update=user_update,
        partil=True,
    )
    return RedirectResponse(url="/user/", status_code=status.HTTP_302_FOUND)


@router.post(
    "/toggle-role/{oid}",
    dependencies=[Depends(RoleRequired(Role.SUPERUSER))],
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    name="users:toggle-role",
    description="Toggle user's role between USER and MODERATOR on each call",
)
async def toggle(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.get_session),
    ],
    user: User = Depends(user_by_oid),
    role: Role = Query(Role),
):
    return await UserService(session).toggle_role(user=user, role=role)
