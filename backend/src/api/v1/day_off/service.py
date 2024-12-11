from typing import List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from models import Overtime, User, OvertimeDayOffLink, Role
from .repository import DayOffRepository
from .schemas import (
    DayOffCreate,
    DayOffOut,
    DayOffExtendedOut,
    PaginatedResponse,
    DayOffUpdatePartil,
    DayOffUpdate,
)
from .overtime_allocator import OvertimeAllocator
from .work_schedule_calculator import WorkScheduleCalculator
from api.v1.user.schemas import UserOut
from models import DayOff


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
            day_off_create=day_off_create
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
    ) -> PaginatedResponse[DayOffOut | DayOffExtendedOut]:
        day_offs = await self.repository.get_all(
            current_user=current_user,
            limit=limit,
            offset=offset,
        )
        if current_user.role == Role.USER:
            day_offs_data = [
                DayOffOut.model_validate(day_off).model_dump() for day_off in day_offs
            ]
            return PaginatedResponse(count=len(day_offs_data), items=day_offs_data)

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
                count=len(extended_day_offs_data), items=extended_day_offs_data
            )

    async def get_day_off_oid(
        self,
        current_user: User,
        oid: uuid.UUID,
    ) -> DayOff:
        day_off: DayOff = await self.repository.get_day_off_oid(
            current_user=current_user,
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
        day_off: DayOff,
        day_off_update: DayOffUpdatePartil,
        partil: bool,
    ) -> DayOffOut:
        day_off = await self.repository.update(
            day_off=day_off,
            day_off_update=day_off_update,
            partil=partil,
        )
        return DayOffOut.model_validate(day_off)
