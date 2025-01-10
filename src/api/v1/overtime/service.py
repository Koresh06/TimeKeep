import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from models import Overtime, Role
from .repository import OvertimeRepository
from .schemas import (
    OvertimeOut,
    OvertimeCreate,
    OvertimeUpdate,
    OvertimeUpdatePartial,
    PaginatedResponse,
    OvertimeExtendedOut,
)
from api.v1.user.schemas import UserOut


class OvertimeService:

    def __init__(self, session: AsyncSession):
        self.repository = OvertimeRepository(session=session)

    async def create(
        self,
        current_user: User,
        overtime_create: OvertimeCreate,
    ) -> OvertimeOut:
        overtime = await self.repository.create(current_user=current_user, overtime_create=overtime_create)
        return OvertimeOut.model_validate(overtime)

    async def get_all(
        self,
        current_user: User,
        limit: int,
        offset: int,
    ) -> PaginatedResponse[OvertimeOut | OvertimeExtendedOut]:
        overtimes, total_count = await self.repository.get_all(
            current_user=current_user,
            limit=limit,
            offset=offset,
        )

        # Если роль пользователя - обычный пользователь, возвращаем стандартные данные
        if current_user.role == Role.USER:
            overtimes_data = [
                OvertimeOut.model_validate(overtime).model_dump()
                for overtime in overtimes
            ]
            return PaginatedResponse(count=total_count, items=overtimes_data)

        # Если роль - модератор или суперюйзер, возвращаем расширенные данные
        else:
            extended_overtimes_data = [
                OvertimeExtendedOut.model_validate(
                    {
                        **OvertimeOut.model_validate(overtime).model_dump(),
                        "user": UserOut.model_validate(overtime.user_rel).model_dump(),
                    }
                )
                for overtime in overtimes
            ]
            return PaginatedResponse(
                count=len(extended_overtimes_data), items=extended_overtimes_data
            )



    async def get_one(self, oid: uuid.UUID) -> Overtime:
        overtime = await self.repository.get_one(oid=oid)
        return overtime

    async def modify(
        self,
        overtime: Overtime,
        overtime_update: OvertimeUpdatePartial,
        partial: bool,
    ) -> OvertimeOut:
        overtime = await self.repository.update(
            overtime=overtime,
            overtime_update=overtime_update,
            partial=partial,
        )
        return OvertimeOut.model_validate(overtime)

    async def replace(
        self,
        overtime: Overtime,
        overtime_update: OvertimeUpdate,
    ) -> OvertimeOut:
        overtime = await self.repository.update(
            overtime=overtime,
            overtime_update=overtime_update,
        )
        return OvertimeOut.model_validate(overtime)
    
    async def delete(self, overtime: Overtime):
        await self.repository.delete(overtime=overtime)
