from uuid import uuid4
from typing import List, TYPE_CHECKING
from enum import Enum

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum as SQLAlchemyEnum
from datetime import datetime

from .base import Base


if TYPE_CHECKING:
    from models import DayOff, Department, Overtime


class Role(Enum):
    USER = "user"
    MODERATOR = "moderator"
    SUPERUSER = "superuser"


class WorkSchedule(Enum):
    DAILY = "daily"     # Ежедневники
    SHIFT = "shift"     # Сменники



class User(Base):
    __tablename__ = "users"
    
    oid: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    department_oid: Mapped[UUID] = mapped_column(UUID, ForeignKey("departments.oid", ondelete="SET NULL"), nullable=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(SQLAlchemyEnum(Role), default=Role.USER)
    work_schedule: Mapped[WorkSchedule] = mapped_column(SQLAlchemyEnum(WorkSchedule))
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    create_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    update_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    department_rel: Mapped["Department"] = relationship("Department", back_populates="user_rel")
    overtime_rel: Mapped["Overtime"] = relationship("Overtime", back_populates="user_rel", cascade="all, delete")
    day_off_rel: Mapped[List["DayOff"]] = relationship("DayOff", back_populates="user_rel", cascade="all, delete")


    def __repr__(self):
        return f"User({self.oid}, {self.username}, {self.department_oid}, {self.create_at}, {self.update_at})"