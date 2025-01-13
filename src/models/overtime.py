from uuid import uuid4
from typing import TYPE_CHECKING, List
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, date

from .base import Base


if TYPE_CHECKING:
    from models import User, Base, OvertimeDayOffLink


class Overtime(Base):
    __tablename__ = "overtimes"

    oid: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    user_oid: Mapped[UUID] = mapped_column(UUID, ForeignKey("users.oid", ondelete="CASCADE"), nullable=False)
    o_date: Mapped[date] = mapped_column(Date, nullable=False)
    hours: Mapped[int] = mapped_column(Integer, nullable=False)
    remaining_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    create_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    update_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    user_rel: Mapped["User"] = relationship("User", back_populates="overtime_rel")
    links: Mapped[List["OvertimeDayOffLink"]] = relationship("OvertimeDayOffLink", back_populates="overtime_rel", cascade="all, delete")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Установим remaining_hours равным hours при создании
        self.remaining_hours = self.hours


    def __repr__(self):
        return f"Overtime(oid={self.oid}, user_oid={self.user_oid}, o_date={self.o_date}, hours={self.hours}, remaining_hours={self.remaining_hours}, description={self.description})"