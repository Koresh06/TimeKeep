from sqlalchemy.ext.asyncio import AsyncSession

from models import Overtime, User, OvertimeDayOffLink
from .repository import DayOffRepository
from .schemas import DayOffCreate, DayOffOut
from .overtime_allocator import OvertimeAllocator
from .work_schedule_calculator import WorkScheduleCalculator


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
        overtimes = await self.repository.get_available_overtimes(user_oid=current_user.oid)
        
        # Выделяем овертаймы для отгула
        selected_overtimes_info = OvertimeAllocator.allocate_hours(overtimes=overtimes, required_hours=required_hours)
        
        # Создаем новый отгул
        new_day_off = await self.repository.create_day_off(day_off_create=day_off_create)
        
        # Создаем связи между отгулом и овертаймами
        overtime_links = []
        for selected_overtime_info in selected_overtimes_info:
            overtime: Overtime = selected_overtime_info['overtime']
            hours_used = selected_overtime_info['hours_used']
            overtime_link = OvertimeDayOffLink(
                overtime_oid=overtime.oid,
                day_off_oid=new_day_off.oid,
                hours_used=hours_used, 
            )
            overtime_links.append(overtime_link)

        # Сохраняем связи в базе данных
        await self.repository.create_overtime_day_off_links(overtime_links)

        # Обновляем овертаймы в базе данных
        await self.repository.update_overtimes(overtimes=[overtime['overtime'] for overtime in selected_overtimes_info])
        
        return DayOffOut.model_validate(new_day_off)



