from uuid import uuid4
from typing import List, TYPE_CHECKING
from enum import Enum

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from fastapi_users_db_sqlalchemy.generics import GUID
from sqlalchemy import DateTime, ForeignKey, String, func
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
    ADMIN = "admin"


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"
    
    department_id: Mapped[UUID] = mapped_column(GUID, ForeignKey("departments.id"), nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(SQLAlchemyEnum(Role), default=Role.USER)
    create_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    update_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    department_rel: Mapped["Department"] = relationship("Department", back_populates="user_rel")
    overtime_rel: Mapped["Overtime"] = relationship("Overtime", back_populates="user_rel")
    day_off_rel: Mapped[List["DayOff"]] = relationship("DayOff", back_populates="user_rel")


    def __repr__(self):
        return f"User({self.id}, {self.username}, {self.department_id}, {self.create_at}, {self.update_at})"