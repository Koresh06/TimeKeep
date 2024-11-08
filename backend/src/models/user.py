from uuid import uuid4
from typing import List, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, String, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from src.models.base import Base

if TYPE_CHECKING:
    from src.models import DayOff, Department


class User(Base):
    __tablename__ = "users"

    oid: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    department_oid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.oid"), nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    _hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    create_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    update_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    department_rel: Mapped["Department"] = relationship("Department", back_populates="user_rel")
    day_off_rel: Mapped[List["DayOff"]] = relationship("DayOff", back_populates="user_rel")


    def __repr__(self):
        return f"User({self.oid}, {self.department_oid}, {self.username}, {self._hashed_password}, {self.is_admin}, {self.is_superuser}, {self.create_at}, {self.update_at})"