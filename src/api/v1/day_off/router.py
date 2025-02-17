from typing import Annotated
from urllib.parse import quote, unquote
import uuid
from fastapi import APIRouter, Depends, Path, Query, Request, status
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    RedirectResponse,
    StreamingResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.infrastructure import db_helper
from src.models import User, Role, DayOff
from src.api.conf_static import templates

from src.api.v1.day_off.schemas import (
    DayOffOut,
    DayOffCreate,
    DayOffExtendedOut,
    PaginatedResponse,
    DayOffUpdate,
    DayOffUpdatePartil,
)
from src.api.v1.day_off.service import DayOffService
from src.api.v1.auth.dependencies import get_current_user
from src.api.v1.auth.permissions import RoleRequired
from src.api.v1.day_off.dependencies import day_off_by_oid
from src.api.v1.day_off.errors import InsufficientOvertimeHours
from src.api.v1.day_off.dependencies import count_notifications_day_offs
from src.middlewares.notification.dependencies import (
    get_unread_notifications_count_user,
)
from src.api.v1.day_off.generate_report import ReportGenerator


router = APIRouter(
    prefix="/day_off",
    tags=["day_off"],
)


@router.get(
    "/create",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR, Role.USER]))],
    name="day_off:create",
    description="Create day_off",
)
async def create_day_off_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    count_day_offs: int = Depends(count_notifications_day_offs),
    notifications_count_user: int = Depends(get_unread_notifications_count_user),
):
    success_message = request.cookies.get("success_message")

    if success_message:
        success_message = unquote(success_message)
    response = templates.TemplateResponse(
        request=request,
        name="day_offs/create.html",
        context={
            "msg": success_message,
            "current_user": current_user,
            "count_day_offs": count_day_offs,
            "notifications_count_user": notifications_count_user,
        },
    )

    if success_message:
        response.delete_cookie("success_message")
    return response


@router.post(
    "/create",
    response_class=RedirectResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR, Role.USER]))],
    name="day_off:create",
    description="Create day_off",
)
async def create_day_off(
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.get_session),
    ],
    day_off_create: DayOffCreate = Depends(DayOffCreate.as_form),
    current_user: User = Depends(get_current_user),
):
    try:
        await DayOffService(session).create(
            current_user=current_user,
            day_off_create=day_off_create,
        )
        response = RedirectResponse(
            url="/day_off/create",
            status_code=status.HTTP_303_SEE_OTHER,
        )
        success_message = quote("✔️ Отгул успешно создан!")
        response.set_cookie(key="success_message", value=success_message)
        return response

    except InsufficientOvertimeHours as e:
        return templates.TemplateResponse(
            request=request,
            name="day_offs/create.html",
            context={"error": str(e), "current_user": current_user},
        )


@router.get(
    "/",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR, Role.USER]))],
    name="day_off:get_all",
    description="Get all day offs",
)
async def get_all_day_offs(
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.get_session),
    ],
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    filter: str = Query(None),
    count_day_offs: int = Depends(count_notifications_day_offs),
    notifications_count_user: int = Depends(get_unread_notifications_count_user),
):
    filter = True if filter == "true" else False

    data = await DayOffService(session).get_all(
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
        name="day_offs/get-all.html",
        context={
            "current_user": current_user,
            "day_offs": data.items,
            "total_count": data.count,
            "total_pages": total_pages,
            "current_page": current_page,
            "limit": limit,
            "offset": offset,
            "filter": filter_value,
            "count_day_offs": count_day_offs,
            "notifications_count_user": notifications_count_user,
        },
    )


@router.get(
    "/notifications",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR]))],
    name="users:notifications",
    description="Notifications page",
)
async def notifications_page(
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
    day_offs = await DayOffService(session).get_all(
        current_user=current_user,
        limit=limit,
        offset=offset,
        is_approved=False,
    )

    total_pages = (day_offs.count + limit - 1) // limit
    current_page = (offset // limit) + 1

    return templates.TemplateResponse(
        request=request,
        name="/day_offs/notifications.html",
        context={
            "current_user": current_user,
            "day_offs": day_offs.items,
            "total_count": day_offs.count,
            "total_pages": total_pages,
            "current_page": current_page,
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
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR]))],
    name="day_off:approve",
    description="Approve day off by id",
)
async def approve_day_off(
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
    day_off: DayOff = Depends(day_off_by_oid),
    current_user: User = Depends(get_current_user),
):
    await DayOffService(session).approve(
        current_user=current_user,
        day_off=day_off,
        is_approved=True,
    )

    return RedirectResponse(
        url="/day_off/notifications", status_code=status.HTTP_302_FOUND
    )


@router.get(
    "/{oid}",
    response_model=DayOffOut | DayOffExtendedOut,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR, Role.USER]))],
    name="day_off:get_one",
    description="Get one day off by id",
)
async def get_one_day_off(
    oid: Annotated[uuid.UUID, Path],
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
    current_user: User = Depends(get_current_user),
):
    return await DayOffService(session).get_one(current_user=current_user, oid=oid)


@router.patch(
    "/{oid}",
    response_model=DayOffOut,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR]))],
    name="day_off:modify",
    description="Modify day off by id",
)
async def modify_day_off(
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
    day_off_update: DayOffUpdatePartil,
    day_off: DayOff = Depends(day_off_by_oid),
    current_user: User = Depends(get_current_user),
):
    return await DayOffService(session).modify(
        current_user=current_user,
        day_off=day_off,
        day_off_update=day_off_update,
        partil=True,
    )


@router.post(
    "/delete/{oid}/me",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR, Role.USER]))],
    name="day_off:delete",
    description="Delete day off by id",
)
async def delete_day_off(
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
    day_off: DayOff = Depends(day_off_by_oid),
    current_user: User = Depends(get_current_user),
):
    await DayOffService(session).delete(
        current_user=current_user, day_off=day_off
    )

    return RedirectResponse("/day_off/", status_code=status.HTTP_303_SEE_OTHER)


@router.post(
    "/delete/{oid}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR]))],
    name="day_off:delete on moderation",
    description="Delete day off on moderation",
)
async def delete_day_off(
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
    day_off: DayOff = Depends(day_off_by_oid),
    current_user: User = Depends(get_current_user),
):
    await DayOffService(session).delete(
        current_user=current_user, day_off=day_off
    )

    return RedirectResponse("/day_off/notifications", status_code=status.HTTP_303_SEE_OTHER)


@router.get(
    "/download_report/{oid}",
    response_class=FileResponse,
    # dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR, Role.USER]))],
    status_code=status.HTTP_200_OK,
    name="day_off:download_report",
)
async def download_report(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.get_session),
    ],
    day_off: DayOff = Depends(day_off_by_oid),
    current_user: User = Depends(get_current_user),
):
    data = await DayOffService(session).generate_report_data(day_off=day_off, current_user=current_user)

    generator = ReportGenerator(data=data)
    file_stream = generator.get_report_bytes()

    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=raport-{day_off.o_date.strftime('%d.%m.%Y')}.docx"},
    )
