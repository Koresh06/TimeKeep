from datetime import datetime
from uuid import uuid4
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID


from .base import Base


if TYPE_CHECKING:
    from models import DayOff,  Overtime



class OvertimeDayOffLink(Base):
    __tablename__ = "overtime_day_off_links"

    oid: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    overtime_oid: Mapped[UUID] = mapped_column(UUID, ForeignKey("overtimes.oid"), nullable=False)
    day_off_oid: Mapped[UUID] = mapped_column(UUID, ForeignKey("day_offs.oid"), nullable=False)
    create_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    update_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    overtime_rel: Mapped["Overtime"] = relationship("Overtime", back_populates="links")
    day_off_rel: Mapped["DayOff"] = relationship("DayOff", back_populates="links")


    def __repr__(self):
        return f"OvertimeDayOffLink(oid={self.oid}, overtime_oid={self.overtime_oid}, day_off_oid={self.day_off_oid})"