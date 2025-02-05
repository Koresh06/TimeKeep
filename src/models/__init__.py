all = (
    "Base"
    "Role",
    "WorkSchedule",
    "User",
    "Department",
    "Overtime",
    "OvertimeDayOffLink"
    "DayOff",
    "Organization"
)

from src.models.base import Base
from src.models.dayoff import DayOff
from src.models.overtime import Overtime
from src.models.overtime_dayoff_link import OvertimeDayOffLink
from src.models.user import User, Role, WorkSchedule
from src.models.department import Department
from src.models.organization import Organization