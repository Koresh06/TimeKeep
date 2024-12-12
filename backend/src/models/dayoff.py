from uuid import uuid4
from typing import TYPE_CHECKING, List
from sqlalchemy import DateTime, Date, ForeignKey, String, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import date, datetime

from .base import Base

if TYPE_CHECKING:
    from models import User, Base, OvertimeDayOffLink


class DayOff(Base):
    __tablename__ = "day_offs"

    oid: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    user_oid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.oid", ondelete="CASCADE"), nullable=False)
    o_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    create_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    update_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    user_rel: Mapped["User"] = relationship("User", back_populates="day_off_rel")
    links: Mapped[List["OvertimeDayOffLink"]] = relationship("OvertimeDayOffLink", back_populates="day_off_rel", cascade="all, delete")



    def __repr__(self):
        return f"DayOff({self.oid}, {self.user_oid}, {self.o_date}, {self.reason}, {self.is_approved}, {self.create_at}, {self.update_at})"