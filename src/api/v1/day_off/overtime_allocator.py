from typing import List
from models import Overtime

from .errors import InsufficientOvertimeHours

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
            raise InsufficientOvertimeHours(required_hours, total_hours)

        return selected_overtimes




