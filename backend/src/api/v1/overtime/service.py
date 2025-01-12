import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from models import Overtime
from .repository import OvertimeRepository
from .schemas import (
    OvertimeOut,
    OvertimeCreate,
    OvertimeUpdate,
    OvertimeUpdatePartial,
    PaginatedResponse,
)


class OvertimeService:

    def __init__(self, session: AsyncSession):
        self.repository = OvertimeRepository(session=session)

    async def create(
        self,
        overtime_create: OvertimeCreate,
    ) -> OvertimeOut:
        overtime = await self.repository.create(overtime_create=overtime_create)
        return OvertimeOut.model_validate(overtime)

    async def get_all(
        self,
        limit: int,
        offset: int,
    ) -> PaginatedResponse[OvertimeOut]:
        overtimes = await self.repository.get_all(limit=limit, offset=offset)
        overtimes_data = [
            OvertimeOut.model_validate(overtime).model_dump() for overtime in overtimes
        ]
        return PaginatedResponse(count=len(overtimes_data), items=overtimes_data)

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
