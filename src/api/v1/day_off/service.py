from typing import List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Overtime, User, OvertimeDayOffLink, Role
from src.api.v1.day_off.repository import DayOffRepository
from src.api.v1.day_off.schemas import (
    DayOffCreate,
    DayOffOut,
    DayOffExtendedOut,
    PaginatedResponse,
    DayOffUpdatePartil,
    DayOffUpdate,
)
from src.api.v1.day_off.overtime_allocator import OvertimeAllocator
from src.api.v1.day_off.work_schedule_calculator import WorkScheduleCalculator
from src.api.v1.user.schemas import UserOut
from src.models import DayOff


class DayOffService:
    def __init__(self, session: AsyncSession):
        self.repository = DayOffRepository(session=session)

    async def create(
        self,
        current_user: User,
        day_off_create: DayOffCreate,
    ) -> DayOffOut:
        """Логика создания отгула."""
        required_hours = WorkScheduleCalculator.get_required_hours(user=current_user)
        overtimes = await self.repository.get_available_overtimes(
            user_oid=current_user.oid
        )

        # Выделяем овертаймы для отгула
        selected_overtimes_info = OvertimeAllocator.allocate_hours(
            overtimes=overtimes, required_hours=required_hours
        )

        # Создаем новый отгул
        new_day_off = await self.repository.create_day_off(
            day_off_create=day_off_create,
            current_user=current_user,
        )

        # Создаем связи между отгулом и овертаймами
        overtime_links = []
        for selected_overtime_info in selected_overtimes_info:
            overtime: Overtime = selected_overtime_info["overtime"]
            hours_used = selected_overtime_info["hours_used"]
            overtime_link = OvertimeDayOffLink(
                overtime_oid=overtime.oid,
                day_off_oid=new_day_off.oid,
                hours_used=hours_used,
            )
            overtime_links.append(overtime_link)

        # Сохраняем связи в базе данных
        await self.repository.create_overtime_day_off_links(overtime_links)

        # Обновляем овертаймы в базе данных
        await self.repository.update_overtimes(
            overtimes=[overtime["overtime"] for overtime in selected_overtimes_info]
        )

        return DayOffOut.model_validate(new_day_off)

    async def get_all(
        self,
        current_user: User,
        limit: int,
        offset: int,
        filter: bool | None = None,
        is_approved: bool | None = None,
    ) -> PaginatedResponse[DayOffOut | DayOffExtendedOut]:
        day_offs, total_count = await self.repository.get_all(
            current_user=current_user,
            limit=limit,
            offset=offset,
            filter=filter,
            is_approved=is_approved,
        )
        if current_user.role == Role.USER:
            day_offs_data = [
                DayOffOut.model_validate(day_off).model_dump() for day_off in day_offs
            ]
            return PaginatedResponse(
                count=total_count,
                items=day_offs_data,
            )

        else:
            extended_day_offs_data = [
                DayOffExtendedOut.model_validate(
                    {
                        **DayOffOut.model_validate(day_off).model_dump(),
                        "user": UserOut.model_validate(day_off.user_rel).model_dump(),
                    }
                )
                for day_off in day_offs
            ]
            return PaginatedResponse(
                count=total_count,
                items=extended_day_offs_data,
            )

    async def get_day_off_oid(
        self,
        oid: uuid.UUID,
    ) -> DayOff:
        day_off: DayOff = await self.repository.get_day_off_oid(
            oid=oid,
        )
        return day_off

    async def get_one(
        self, current_user: User, oid: int
    ) -> DayOffOut | DayOffExtendedOut:
        day_off: DayOff = await self.repository.get_one(
            current_user=current_user, oid=oid
        )
        if current_user.role == Role.USER:
            return DayOffOut.model_validate(day_off)
        else:
            return DayOffExtendedOut.model_validate(
                {
                    **DayOffOut.model_validate(day_off).model_dump(),
                    "user": UserOut.model_validate(day_off.user_rel).model_dump(),
                }
            )

    async def modify(
        self,
        current_user: User,
        day_off: DayOff,
        day_off_update: DayOffUpdatePartil,
        partil: bool,
    ) -> DayOffOut:
        day_off = await self.repository.update(
            current_user=current_user,
            day_off=day_off,
            day_off_update=day_off_update,
            partil=partil,
        )
        return DayOffOut.model_validate(day_off)

    async def delete(self, current_user: User, day_off: DayOff):
        await self.repository.delete(current_user=current_user, day_off=day_off)


    async def approve(self, current_user: User, day_off: DayOff, is_approved: bool):
        day_off = await self.repository.approve(
            current_user=current_user,
            day_off=day_off,
            is_approved=is_approved,
        )
        return DayOffOut.model_validate(day_off)


    async def count_notifications(self, current_user: User) -> int:
        return await self.repository.count_notifications_stmt_is_unapproved(current_user=current_user)