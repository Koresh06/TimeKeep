from uuid import uuid4
from typing import List, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, String, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from models.base import Base

if TYPE_CHECKING:
    from models import User


class DayOff(Base):
    __tablename__ = "day_offs"

    oid: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    user_oid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.oid"), nullable=False)
    start_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[bool] = mapped_column(Boolean, default=True)
    create_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    update_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    user_rel: Mapped["User"] = relationship("User", back_populates="day_off_rel")


    def __repr__(self):
        return f"DayOff({self.oid}, {self.user_oid}, {self.start_datetime}, {self.end_datetime}, {self.reason}, {self.status}, {self.create_at}, {self.update_at})"