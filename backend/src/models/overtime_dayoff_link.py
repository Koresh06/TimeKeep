from uuid import uuid4
from typing import TYPE_CHECKING
from fastapi_users_db_sqlalchemy.generics import GUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID


from .base import Base


if TYPE_CHECKING:
    from models import DayOff,  Overtime



class OvertimeDayOffLink(Base):
    __tablename__ = "overtime_day_off_links"

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid4)
    overtime_id: Mapped[UUID] = mapped_column(GUID, ForeignKey("overtimes.id"), nullable=False)
    day_off_id: Mapped[UUID] = mapped_column(GUID, ForeignKey("day_offs.id"), nullable=False)

    overtime_rel: Mapped["Overtime"] = relationship("Overtime", back_populates="links")
    day_off_rel: Mapped["DayOff"] = relationship("DayOff", back_populates="links")