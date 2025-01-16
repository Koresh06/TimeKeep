import uuid

from typing import List, Tuple
from fastapi import HTTPException, status
from sqlalchemy import Result, func, select, Select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from core.repo.base import BaseRepo
from models import DayOff, Overtime, OvertimeDayOffLink, User, Role

from .schemas import DayOffCreate, DayOffUpdatePartil, DayOffUpdate
from .errors import DayOffNotFoundError, DepartmentPermissionError


class DayOffRepository(BaseRepo):

    async def get_available_overtimes(
        self,
        user_oid: uuid.UUID,
    ) -> List[Overtime]:
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

    async def create_day_off(self, day_off_create: DayOffCreate, current_user: User) -> DayOff:
        """Создание нового отгула."""
        try:
            new_day_off = DayOff(
                user_oid=current_user.oid,
                o_date=day_off_create.o_date,
                reason=day_off_create.reason,
            )
            self.session.add(new_day_off)
            await self.session.commit()
            await self.session.refresh(new_day_off)
            return new_day_off
        except IntegrityError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    async def create_overtime_day_off_links(
        self,
        overtime_links: List[OvertimeDayOffLink],
    ):
        """Создание связи между овертаймами и отгулом."""
        try:
            for link in overtime_links:
                link.hours_used = link.hours_used
            self.session.add_all(overtime_links)
            await self.session.commit()
        except IntegrityError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    async def update_overtimes(
        self,
        overtimes: List[Overtime],
    ) -> None:
        """Обновить записи overtimes в базе данных."""
        try:
            for overtime in overtimes:
                if overtime.remaining_hours == 0:
                    overtime.is_used = True
            await self.session.commit()
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    async def _build_stmt_for_role(
    self,
    current_user: User,
    stmt: Select,
    oid: int = None,
    ) -> Select:
        """Общая логика для построения запроса в зависимости от роли пользователя."""
        if current_user.role == Role.USER:
            stmt = stmt.where(DayOff.user_oid == current_user.oid)
            if oid:
                stmt = stmt.where(DayOff.oid == oid)

        elif current_user.role == Role.MODERATOR:
            # Уточняем связь с User через `join` (явная связь через FK)
            stmt = stmt.join(User, User.oid == DayOff.user_oid)
            stmt = stmt.where(User.department_oid == current_user.department_oid)
            if oid:
                stmt = stmt.where(DayOff.oid == oid)

        elif current_user.role == Role.SUPERUSER:
            if oid:
                stmt = stmt.where(DayOff.oid == oid)

        stmt = stmt.options(joinedload(DayOff.user_rel))  # Загрузка связанных пользователей
        return stmt
    
    async def count_notifications_stmt_is_unapproved(
        self,
        current_user: User,
    ) -> int:
        stmt = select(func.count()).select_from(DayOff)
        stmt = stmt.filter(DayOff.is_approved == False)

        if current_user.role == Role.USER:
            stmt = stmt.filter(DayOff.user_oid == current_user.oid)
        elif current_user.role == Role.MODERATOR:
            stmt = stmt.join(User, User.oid == DayOff.user_oid)
            stmt = stmt.filter(User.department_oid == current_user.department_oid)
        elif current_user.role == Role.SUPERUSER:
            pass

        result = await self.session.scalar(stmt)

        return result


    async def get_all(
        self,
        current_user: User,
        limit: int,
        offset: int,
        filter: bool | None = None,
        is_approved: bool | None = None,
    ) -> Tuple[List[DayOff], int]:
        """Получение всех отгулов с фильтрацией по дате и статусу, включая переработки."""
    
        try:
            stmt_count = select(func.count()).select_from(DayOff)
    
            if filter is not None:
                if filter: 
                    stmt_count = stmt_count.filter(DayOff.o_date < func.current_date())
                else: 
                    stmt_count = stmt_count.filter(DayOff.o_date >= func.current_date())
    
            if is_approved is not None:
                stmt_count = stmt_count.filter(DayOff.is_approved == is_approved)

            total_count = await self.session.scalar(stmt_count)
    
            stmt = (
                select(DayOff)
                .limit(limit)
                .offset(offset)
                .options(
                    selectinload(DayOff.links).selectinload(OvertimeDayOffLink.day_off_rel)
                )
                .order_by(DayOff.create_at.desc())
            )
    
            if filter is not None:
                if filter: 
                    stmt = stmt.filter(DayOff.o_date < func.current_date())
                else:
                    stmt = stmt.filter(DayOff.o_date >= func.current_date())
    
            if is_approved is not None:
                stmt = stmt.filter(DayOff.is_approved == is_approved)
    
            # Добавляем фильтрацию в зависимости от роли
            stmt = await self._build_stmt_for_role(current_user, stmt)
            
            result: Result = await self.session.scalars(stmt)
    
            return result.all(), total_count
    
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")



    async def get_day_off_oid(
        self,
        oid: uuid.UUID,
    ) -> DayOff:
        """Получение отгула по oid, проверка на существование."""
        try:
            stmt = select(DayOff).options(selectinload(DayOff.user_rel)).where(DayOff.oid == oid)
            day_off = await self.session.scalar(stmt)
            if not day_off:
                raise DayOffNotFoundError(oid)
            return day_off
        except DayOffNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Day off with oid {oid} not found",
            )
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    async def get_one(
        self,
        current_user: User,
        oid: int,
    ) -> DayOff:
        """Получение одного отгула по oid."""
        try:
            stmt = select(DayOff)
            stmt = await self._build_stmt_for_role(
                current_user=current_user, stmt=stmt, oid=oid
            )

            day_off = await self.session.scalar(stmt)

            if not day_off:
                raise DayOffNotFoundError(oid)

            return day_off

        except DayOffNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Day off with oid {oid} not found",
            )
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    async def update(
        self,
        current_user: User,
        day_off: DayOff,
        day_off_update: DayOffUpdate | DayOffUpdatePartil,
        partil: bool = False,
    ) -> DayOff:
        """Обновить отгул."""
        try:
            if current_user.role == Role.MODERATOR and current_user.department_oid != day_off.user_rel.department_oid:
                raise DepartmentPermissionError()
            if partil:
                for attr, value in day_off_update.model_dump(
                    exclude_unset=partil
                ).items():
                    setattr(day_off, attr, value)
            else:
                day_off = DayOff.model_validate(day_off_update)
            await self.session.commit()
            return day_off
        except IntegrityError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database error: {str(e)}",
            )


    async def delete(self, current_user: User, day_off: DayOff):
        """Удалить отгул."""
        try:

            if current_user.role == Role.MODERATOR and current_user.department_oid != day_off.user_rel.department_oid:
                raise DepartmentPermissionError()
            
            await self.session.delete(day_off)
            await self.session.commit()

        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        

    async def approve(self, day_off: DayOff, is_approved: bool, current_user: User) -> DayOff:
        """Подтвердить отгул с проверкой отдела."""
        try:
            if current_user.role == Role.MODERATOR and current_user.department_oid != day_off.user_rel.department_oid:
                raise DepartmentPermissionError()

            day_off.is_approved = is_approved
            await self.session.commit()
            return day_off
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")