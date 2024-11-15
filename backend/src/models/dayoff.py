from uuid import uuid4
from typing import TYPE_CHECKING, List
from sqlalchemy import DateTime, ForeignKey, String, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from fastapi_users_db_sqlalchemy.generics import GUID
from datetime import datetime

from .base import Base

if TYPE_CHECKING:
    from models import User, Base, OvertimeDayOffLink


class DayOff(Base):
    __tablename__ = "day_offs"

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    create_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    update_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    user_rel: Mapped["User"] = relationship("User", back_populates="day_off_rel")
    links: Mapped[List["OvertimeDayOffLink"]] = relationship("OvertimeDayOffLink", back_populates="day_off_rel")



    def __repr__(self):
        return f"DayOff({self.id}, {self.user_id}, {self.date} {self.reason}, {self.is_approved}, {self.create_at}, {self.update_at})"