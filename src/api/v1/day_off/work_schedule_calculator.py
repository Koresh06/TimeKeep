from fastapi import HTTPException

from src.models import User, WorkSchedule


class WorkScheduleCalculator:
    
    @staticmethod
    def get_required_hours(user: User) -> int:
        if user.work_schedule == WorkSchedule.SHIFT:
            return 24
        elif user.work_schedule == WorkSchedule.DAILY:
            return 8
        else:
            raise HTTPException(
                status_code=400,
                detail="Неизвестный тип пользователя.",
            )
