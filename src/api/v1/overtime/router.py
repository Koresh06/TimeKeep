from datetime import date, datetime
from uuid import UUID
from fastapi import APIRouter, HTTPException, Response, status, Depends, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import quote, unquote

from api.conf_static import templates
from api.v1.auth.dependencies import get_current_user, get_is_authenticated
from models.user import User
from models import Overtime, Role
from core.session import get_async_session
from api.v1.auth.permissions import RoleRequired
from .service import OvertimeService
from .schemas import (
    OvertimeOut,
    OvertimeCreate,
    OvertimeUpdate,
    OvertimeUpdatePartial,
    PaginatedResponse,
)
from .dependencies import overtime_by_oid
from middlewares.notification.dependencies import get_unread_notifications_count


router = APIRouter(
    prefix="/overtime", tags=["overtime"], dependencies=[Depends(get_current_user)]
)


@router.get(
    "/create",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR, Role.USER]))],
    name="overtime:create",
    description="Create overtime",
)
async def create_overtime_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    notifications_count: int = Depends(get_unread_notifications_count),
):
    success_message = request.cookies.get("success_message")
    # Декодируем сообщение из куки
    if success_message:
        success_message = unquote(success_message)
    response = templates.TemplateResponse(
        request=request,
        name="overtimes/create.html",
        context={
            "msg": success_message,
            "current_user": current_user,
            "notifications_count": notifications_count
        },
    )
    # Удаляем cookie, чтобы сообщение не отображалось снова
    if success_message:
        response.delete_cookie("success_message")
    return response


@router.post(
    "/create",
    response_class=HTMLResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR, Role.USER]))],
    name="overtime:create",
    description="Create overtime",
)
async def create_overtime(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: User = Depends(get_current_user),
    overtime_create: OvertimeCreate = Depends(OvertimeCreate.as_form),
):
    try:
        await OvertimeService(session).create(
            current_user=current_user,
            overtime_create=overtime_create,
        )
        response = RedirectResponse(
            url="/overtime/create",
            status_code=status.HTTP_303_SEE_OTHER,
        )
        success_message = quote("✔️ Переработка успешно создана!")
        response.set_cookie(key="success_message", value=success_message)
        return response

    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="overtimes/create.html",
            context={
                "error": str(e),
                "current_user": current_user,
            },
        )


@router.get(
    "/",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR, Role.USER]))],
    name="overtime:get_all",
    description="Get all overtimes",
)
async def get_all_overtimes(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    filter: str = Query(None),
    notifications_count: int = Depends(get_unread_notifications_count),
):
    

    filter = True if filter == "true" else False

    data = await OvertimeService(session).get_all(
        current_user=current_user,
        limit=limit,
        offset=offset,
        filter=filter,
    )

    total_pages = (data.count + limit - 1) // limit
    current_page = (offset // limit) + 1

    filter_value = "true" if filter else "false"

    return templates.TemplateResponse(
        request=request,
        name="overtimes/get-all.html",
        context={
            "current_user": current_user,
            "overtimes": data.items,
            "total_count": data.count,
            "total_pages": total_pages,
            "current_page": current_page,
            "limit": limit,
            "offset": offset,
            "filter": filter_value,
            "notifications_count": notifications_count,
        },
    )


@router.get(
    "/edit/{oid}",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR, Role.USER]))],
    name="overtime:modify",
    description="Modify overtime",
)
async def edit_overtime_page(
    request: Request,
    overtime: Overtime = Depends(overtime_by_oid),
    current_user: User = Depends(get_current_user),
    notifications_count: int = Depends(get_unread_notifications_count),
):
    return templates.TemplateResponse(
        request=request,
        name="overtimes/edit.html",
        context={
            "current_user": current_user,
            "overtime": overtime,
            "notifications_count": notifications_count
        },
    )


@router.post(
    "/edit/{oid}",
    response_class=RedirectResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR]))],
    name="overtime:modify",
    description="Modify overtime",
)
async def modify_overtime(
    session: Annotated[
        AsyncSession,
        Depends(get_async_session),
    ],
    overtime_update: OvertimeUpdatePartial = Depends(OvertimeUpdatePartial.as_form),
    overtime: Overtime = Depends(overtime_by_oid),
):
    await OvertimeService(session).modify(
        overtime=overtime,
        overtime_update=overtime_update,
        partial=True,
    )

    return RedirectResponse(url="/overtime/", status_code=status.HTTP_302_FOUND)


@router.post(
    "/delete/{oid}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR, Role.USER]))],
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

    return RedirectResponse(url="/overtime/", status_code=status.HTTP_303_SEE_OTHER)
