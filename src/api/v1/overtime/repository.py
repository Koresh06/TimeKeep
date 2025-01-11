import uuid

from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy import Select, func, select, Result
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


from models.user import User
from core.repo.base import BaseRepo
from models import Overtime, Role

from .schemas import OvertimeCreate, OvertimeUpdate, OvertimeUpdatePartial


class OvertimeRepository(BaseRepo):

    async def create(
        self,
        current_user: User,
        overtime_create: OvertimeCreate,
    ) -> Overtime:
        try:
            overtime = Overtime(
                user_oid=current_user.oid,
                o_date=overtime_create.o_date,
                hours=overtime_create.hours,
                description=overtime_create.description,
            )
            self.session.add(overtime)
            await self.session.commit()
            await self.session.refresh(overtime)
            return overtime
        except IntegrityError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    async def _build_stmt_for_role(
            self,
            current_user: User,
            stmt: Select,
            oid: int = None,
        ) -> Select:
        """Общая логика для построения запроса в зависимости от роли пользователя."""

        # Если пользователь — обычный USER, фильтруем данные только для текущего пользователя
        if current_user.role == Role.USER:
            if oid:
                stmt = stmt.where(
                    (Overtime.oid == oid) & (Overtime.user_oid == current_user.oid)
                )
            else:
                stmt = stmt.where(Overtime.user_oid == current_user.oid)

        # Если пользователь — MODERATOR, фильтруем данные по отделу пользователя
        elif current_user.role == Role.MODERATOR:
            if oid:
                stmt = (
                    stmt.join(User)
                    .where(
                        (User.department_oid == current_user.department_oid)
                        & (Overtime.oid == oid)
                    )
                    .options(joinedload(Overtime.user_rel))
                )
            else:
                stmt = (
                    stmt.join(User)
                    .where(User.department_oid == current_user.department_oid)
                    .options(joinedload(Overtime.user_rel))
                )

        # Если пользователь — SUPERUSER, нет ограничений на данные
        elif current_user.role == Role.SUPERUSER:
            if oid:
                stmt = stmt.options(joinedload(Overtime.user_rel)).where(
                    Overtime.oid == oid
                )
            else:
                stmt = stmt.options(joinedload(Overtime.user_rel))

        return stmt


    async def get_all(
        self,
        current_user: User,
        limit: int,
        offset: int,
        is_used: bool = None,
    ) -> List[Overtime]:
        try:
            stmt_count = select(func.count()).select_from(Overtime)
            if is_used is not None:
                stmt_count = stmt_count.filter(Overtime.is_used == is_used)
            total_count = await self.session.scalar(stmt_count)

            stmt = select(Overtime).limit(limit).offset(offset)
            if is_used is not None:
                stmt = stmt.filter(Overtime.is_used == is_used)

            stmt = await self._build_stmt_for_role(current_user, stmt)
            result: Result = await self.session.scalars(stmt)

            return result.all(), total_count
        
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


    async def get_one(
        self,
        oid: uuid.UUID,
    ) -> Optional[Overtime]:
        try:
            stmt = select(Overtime).where(Overtime.oid == oid)
            result: Result = await self.session.scalar(stmt)
            return result
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


    async def update(
        self,
        overtime: Overtime,
        overtime_update: OvertimeUpdate | OvertimeUpdatePartial,
        partial: bool = False,
    ) -> Optional[Overtime]:
        try:
            for key, value in overtime_update.model_dump(exclude_unset=partial).items():
                setattr(overtime, key, value)

            await self.session.commit()
            await self.session.refresh(overtime)
            return overtime
        except IntegrityError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    async def delete(self, overtime: Overtime):
        try:
            await self.session.delete(overtime)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")