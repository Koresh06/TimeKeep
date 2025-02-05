from uuid import uuid4
from typing import List, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from src.models.base import Base

if TYPE_CHECKING:
    from src.models import User, Base, Organization


class Department(Base):
    __tablename__ = "departments"

    oid: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    organization_oid: Mapped[UUID] = mapped_column(UUID, ForeignKey("organizations.oid", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    create_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    update_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    organization_rel: Mapped["Organization"] = relationship("Organization", back_populates="department_rel")
    user_rel: Mapped[List["User"]] = relationship("User", back_populates="department_rel")

    


    def __repr__(self):
        return f"Department({self.oid}, {self.name}, {self.description}, {self.create_at}, {self.update_at})"