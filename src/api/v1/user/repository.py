from datetime import date
import uuid

from typing import List, Optional, Tuple
from fastapi import HTTPException
from sqlalchemy import and_, func, select, Result
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.core.repo.base import BaseRepo
from src.models import User, Role, Overtime, DayOff
from src.api.v1.user.schemas import UserCreate, UserUpdatePartial, UserUpdate, SuperUserCreate
from src.api.v1.auth.security import get_password_hash


class UserRepository(BaseRepo):

    async def get_user_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        result: Result = await self.session.scalar(stmt)
        return result

    async def get_user_by_id(self, oid: uuid.UUID) -> Optional[User]:
        stmt = select(User).where(User.oid == oid)
        result: Result = await self.session.scalar(stmt)
        return result

    async def create(self, data: UserCreate) -> User:
        try:
            hashed_password = get_password_hash(data.password)

            user_data = data.model_dump(exclude={"password"})
            user_data["hashed_password"] = hashed_password
            user = User(**user_data)

            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except IntegrityError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
    
    async def create_superuser(self, data: SuperUserCreate) -> User:
        try:
            hashed_password = get_password_hash(data.password)

            user_data = data.model_dump(exclude={"password"})
            user_data["hashed_password"] = hashed_password
            user = User(**user_data)
            user.is_active = True

            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except IntegrityError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    async def get_all(
        self,
        limit: int,
        offset: int,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[User], int]:
        try:
            stmt_count = select(func.count())
            stmt = select(User).options(selectinload(User.department_rel), selectinload(User.organization_rel))

            if is_active is not None:
                stmt_count = stmt_count.where(User.is_active == is_active)
                stmt = stmt.where(User.is_active == is_active)

            total_count = await self.session.scalar(stmt_count)

            stmt = (
                stmt
                .limit(limit)
                .offset(offset)
                .order_by(User.create_at.desc())
            )
            result = await self.session.scalars(stmt)

            return result.all(), total_count

        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


    async def approve_or_reject_user(
        self,
        user: User,
        is_active: bool,
    ) -> User:
        try:
            user.is_active = is_active
            await self.session.commit()
            await self.session.refresh(user)
            return user
        
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


    async def count_all(self, filters: List) -> int:
        query = select(func.count(User.oid)).where(and_(*filters))
        result = await self.session.execute(query)
        return result.scalar()

    async def get_one(self, oid: uuid.UUID) -> User:
        try:
            stmt = select(User).where(User.oid == oid)
            result: Result = await self.session.scalar(stmt)
            return result
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    async def update(
        self,
        user: User,
        user_update: UserUpdate | UserUpdatePartial,
        partil: bool = False,
    ) -> User:
        # try:
            for key, value in user_update.model_dump(exclude_unset=partil).items():
                setattr(user, key, value)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        # except SQLAlchemyError as e:
        #     await self.session.rollback()
        #     raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    async def delete(self, user: User):
        try:
            await self.session.delete(user)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    async def toggle_role(self, user: User, role: Role) -> User:
        try:
            # user.role = Role.MODERATOR if user.role == Role.USER else Role.USER
            if user.role == role:
                raise HTTPException(
                    status_code=400, detail="User already has this role"
                )
            user.role = role
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


    async def get_statistics_current_user(self, current_user: User, selected_year: int = None):
        # Получаем список всех доступных лет с переработками
        result = await self.session.execute(
            select(func.extract("year", Overtime.o_date).distinct())
            .where(Overtime.user_oid == current_user.oid)
        )
        available_years = [int(row[0]) for row in result.fetchall() if row[0] is not None]

        # Если год не выбран, берем последний доступный
        selected_year = selected_year or (max(available_years) if available_years else date.today().year)

        # Получаем часы переработок по месяцам для выбранного года
        result = await self.session.execute(
            select(
                func.extract("month", Overtime.o_date),
                func.sum(Overtime.hours)
            )
            .where(
                Overtime.user_oid == current_user.oid,
                func.extract("year", Overtime.o_date) == selected_year
            )
            .group_by(func.extract("month", Overtime.o_date))
        )

        monthly_overtime = {int(month): hours for month, hours in result.fetchall()}

        # Получаем общую статистику (оставляем как было)
        result = await self.session.execute(
            select(
                func.count(Overtime.oid),
                func.count().filter(Overtime.is_used == True),
                func.count().filter(Overtime.is_used == False),
                func.sum(Overtime.remaining_hours),
            ).where(Overtime.user_oid == current_user.oid)
        )
        total_overtimes, used_overtimes, remaining_overtimes, total_remaining_hours = result.first()

        # Получаем данные об отгулах
        today = date.today()
        result = await self.session.execute(
            select(
                func.count(DayOff.oid),
                func.count().filter(DayOff.o_date < today),
                func.count().filter(DayOff.o_date >= today),
            ).where(DayOff.user_oid == current_user.oid)
        )
        total_day_offs, used_day_offs, remaining_day_offs = result.first()

        return {
            "years": available_years,
            "selected_year": selected_year,
            "overtime": {
                "total": total_overtimes,
                "used": used_overtimes,
                "remaining": remaining_overtimes,
                "total_remaining_hours": total_remaining_hours,
                "monthly": monthly_overtime,
            },
            "day_off": {
                "total": total_day_offs,
                "used": used_day_offs,
                "remaining": remaining_day_offs,
            },
        }

