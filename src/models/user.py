from uuid import uuid4
from typing import List, TYPE_CHECKING
from enum import Enum

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum as SQLAlchemyEnum
from datetime import datetime

from src.models.base import Base


if TYPE_CHECKING:
    from src.models import DayOff, Department, Overtime, Organization


class Role(Enum):
    USER = "user" # Пользователь
    MODERATOR = "moderator" # Модератор
    SUPERUSER = "superuser" # Суперпользователь


class WorkSchedule(Enum):
    DAILY = "daily"     # Ежедневники
    SHIFT = "shift"     # Сменники



class User(Base):
    __tablename__ = "users"
    
    oid: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    organization_oid: Mapped[UUID] = mapped_column(UUID, ForeignKey("organizations.oid", ondelete="SET NULL"), nullable=True)
    department_oid: Mapped[UUID] = mapped_column(UUID, ForeignKey("departments.oid", ondelete="SET NULL"), nullable=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(SQLAlchemyEnum(Role), default=Role.USER)
    work_schedule: Mapped[WorkSchedule] = mapped_column(SQLAlchemyEnum(WorkSchedule))
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[str] = mapped_column(String(255), nullable=False)
    rank: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    create_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    update_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    organization_rel: Mapped["Organization"] = relationship("Organization", back_populates="user_rel")
    department_rel: Mapped["Department"] = relationship("Department", back_populates="user_rel")
    overtime_rel: Mapped[List["Overtime"]] = relationship("Overtime", back_populates="user_rel", cascade="all, delete")
    day_off_rel: Mapped[List["DayOff"]] = relationship("DayOff", back_populates="user_rel", cascade="all, delete")



    def __repr__(self):
        return f"User({self.oid}, {self.organization_oid}, {self.department_oid}, {self.username}, {self.full_name}, {self.role}, {self.work_schedule}, {self.hashed_password}, {self.position}, {self.is_active}, {self.create_at}, {self.update_at})"