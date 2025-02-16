from typing import List, Annotated
from urllib.parse import quote, unquote
from fastapi import APIRouter, Query, Request, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.day_off.dependencies import count_notifications_day_offs
from src.core.session import get_async_session
from src.api.conf_static import templates
from src.api.v1.organization.schemas import OrganizationCreate
from src.api.v1.organization.service import OrganizationService
from src.api.v1.auth.permissions import RoleRequired
from src.api.v1.auth.dependencies import get_current_user
from src.middlewares.notification.dependencies import get_unread_notifications_count_user
from src.models.user import User, Role


router = APIRouter(
    prefix="/organization",
    tags=["organization"],
)


@router.get(
    "/create",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER]))],
    name="organization:create",
    description="Create organization",
)
async def create_organization(
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
        name="organizations/create.html",
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
    status_code=status.HTTP_302_FOUND,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER]))],
    name="organization:create",
    description="Create organization",
)
async def create_organization(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: User = Depends(get_current_user),
    organization_create: OrganizationCreate = Depends(OrganizationCreate.as_form),
):
    try:
        await OrganizationService(session).create(
            organization_create=organization_create,
        )
        response = RedirectResponse(
            url="/organization/create",
            status_code=status.HTTP_303_SEE_OTHER,
        )
        success_message = quote("✔️ Организация успешно создана!")
        response.set_cookie(key="success_message", value=success_message)
        return response
    
    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="organizations/create.html",
            context={
                "error": str(e),
                "current_user": current_user,
            },
        )


@router.get(
    "/",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER]))],
    name="organization:get_all",
    description="Get all organizations",
)
async def get_all_organizations(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    request: Request,
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    count_day_offs: int = Depends(count_notifications_day_offs),
    notifications_count_user: int = Depends(get_unread_notifications_count_user),
):
    organizations = await OrganizationService(session).get_all(limit=limit, offset=offset)

    total_pages = (organizations.count + limit - 1) // limit
    current_page = (offset // limit) + 1

    return templates.TemplateResponse(
        request=request,
        name="organizations/get-all.html",
        context={
            "organizations": organizations.items,
            "total_pages": total_pages,
            "current_page": current_page,
            "limit": limit,
            "offset": offset,
            "current_user": current_user,
            "count_day_offs": count_day_offs,
            "notifications_count_user": notifications_count_user,
        },
    )