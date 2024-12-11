import uuid

from typing import List
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from core.repo.base import BaseRepo
from models import DayOff, Overtime, OvertimeDayOffLink, User, Role

from .schemas import DayOffCreate


class DayOffRepository(BaseRepo):

    async def get_available_overtimes(self, user_oid: uuid.UUID) -> List[Overtime]:
        """Получение доступных овертаймов."""
        try:
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
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    async def create_day_off(self, day_off_create: DayOffCreate) -> DayOff:
        """Создание нового отгула."""
        try:
            new_day_off = DayOff(**day_off_create.model_dump())
            self.session.add(new_day_off)
            await self.session.commit()
            await self.session.refresh(new_day_off)
            return new_day_off
        except IntegrityError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    async def create_overtime_day_off_links(
        self, overtime_links: List[OvertimeDayOffLink]
    ):
        """Создание связи между овертаймами и отгулом."""
        try:
            for link in overtime_links:
                link.hours_used = link.hours_used
            self.session.add_all(overtime_links)
            await self.session.commit()
        except IntegrityError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    async def update_overtimes(self, overtimes: List[Overtime]) -> None:
        """Обновить записи overtimes в базе данных."""
        try:
            for overtime in overtimes:
                if overtime.remaining_hours == 0:
                    overtime.is_used = True
            await self.session.commit()
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    async def get_all(
        self,
        current_user: User,
        limit: int,
        offset: int,
    ) -> List[DayOff]:
        """Получение всех отгулов."""
        try:
            stmt = select(DayOff).limit(limit).offset(offset)

            if current_user.role == Role.USER:
                stmt = stmt.where(DayOff.user_oid == current_user.oid)

            elif current_user.role == Role.MODERATOR:
                stmt = (
                    stmt
                    .join(User)
                    .where(User.department_oid == current_user.department_oid)
                    .options(joinedload(DayOff.user_rel))
                )

            elif current_user.role == Role.SUPERUSER:
                stmt = stmt.options(joinedload(DayOff.user_rel))

            day_offs = await self.session.scalars(stmt)

            return day_offs
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

