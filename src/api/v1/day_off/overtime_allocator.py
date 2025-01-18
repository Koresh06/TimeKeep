from typing import List
from src.models import Overtime

from src.api.v1.day_off.errors import InsufficientOvertimeHours

class OvertimeAllocator:

    @staticmethod
    def allocate_hours(overtimes: List[Overtime], required_hours: int) -> List[dict]:
        """
        Распределяет часы из овертаймов на отгул и возвращает список словарей с овертаймами и использованными часами.
        """
        total_hours = 0
        selected_overtimes: List[dict] = []

        for overtime in overtimes:
            available_hours = overtime.remaining_hours

            if total_hours + available_hours >= required_hours:
                needed_hours = required_hours - total_hours
                overtime.remaining_hours -= needed_hours 
                total_hours += needed_hours
                selected_overtimes.append({
                    'overtime': overtime,
                    'hours_used': needed_hours  
                })
                break  
            else:
                total_hours += available_hours
                overtime.remaining_hours = 0  
                selected_overtimes.append({
                    'overtime': overtime,
                    'hours_used': available_hours 
                })

        if total_hours < required_hours:
            raise InsufficientOvertimeHours()

        return selected_overtimes




