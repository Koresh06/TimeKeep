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
):
    success_message = request.cookies.get("success_message")
    # Декодируем сообщение из куки
    if success_message:
        success_message = unquote(success_message)
    response = templates.TemplateResponse(
        "overtimes/create.html",
        {
            "request": request,
            "msg": success_message,
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
            context={"error": str(e)},
        )


def serialize_data(data):
    if isinstance(data, (datetime, date)):  # Проверяем на datetime или date
        return data.strftime("%Y-%m-%d")  # Преобразуем в строку в формате 'YYYY-MM-DD'
    elif isinstance(data, UUID):  # Проверяем на UUID
        return str(data)  # Преобразуем UUID в строку
    return data  # Если тип данных не подходит, возвращаем его как есть


# Применим сериализацию ко всем полям данных
def serialize_overtimes(overtimes):
    return [
        {key: serialize_data(value) for key, value in overtime.items()}
        for overtime in overtimes
    ]


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
    is_used: bool = Query(None),
):
    # Получаем все овертаймы и общее количество записей
    data = await OvertimeService(session).get_all(
        current_user=current_user,
        limit=limit,
        offset=offset,
        is_used=is_used,
    )

    # Сериализуем данные
    # serialized_overtimes = serialize_overtimes(data.items)

    # Вычисляем количество страниц
    total_pages = (data.count + limit - 1) // limit  # Округляем вверх
    current_page = (offset // limit) + 1  # Текущая страница

    return templates.TemplateResponse(
        request=request,
        name="overtimes/get-all.html",  # Путь к частичному шаблону таблицы
        context={
            "overtimes": data.items,
            "total_count": data.count,
            "total_pages": total_pages,
            "current_page": current_page,
            "limit": limit,
            "offset": offset,
            "is_authenticated": current_user,
        },
    )


@router.get(
    "/{oid}",
    response_model=OvertimeOut,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR, Role.USER]))],
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
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR]))],
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
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR]))],
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
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR]))],
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
