import uuid

from typing import List
from sqlalchemy import select

from core.repo.base import BaseRepo
from models import DayOff, Overtime, OvertimeDayOffLink

from .schemas import DayOffCreate


class DayOffRepository(BaseRepo):

    async def get_available_overtimes(self, user_oid: uuid.UUID) -> List[Overtime]:
        """Получение доступных овертаймов."""
        query = (
            select(Overtime)
            .where(
                Overtime.user_oid == user_oid,
                Overtime.is_used == False,
            )
            .order_by(Overtime.o_date.asc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create_day_off(self, day_off_create: DayOffCreate) -> DayOff:
        """Создание нового отгула."""
        new_day_off = DayOff(**day_off_create.model_dump())
        self.session.add(new_day_off)
        await self.session.commit()
        await self.session.refresh(new_day_off)
        return new_day_off

    async def create_overtime_day_off_links(self, overtime_links: List[OvertimeDayOffLink]):
        """Создание связи между овертаймами и отгулом."""
        for link in overtime_links:
            link.hours_used = link.hours_used 
        self.session.add_all(overtime_links) 
        await self.session.commit() 
        
    async def update_overtimes(self, overtimes: List[Overtime]) -> None:
        """
        Обновить записи overtimes в базе данных.
        """
        for overtime in overtimes:
            if overtime.remaining_hours == 0:
                overtime.is_used = True
        await self.session.commit()
