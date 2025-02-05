from datetime import datetime
from uuid import uuid4
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, String, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.models.base import Base


if TYPE_CHECKING:
    from src.models import Department, User




class Organization(Base):
    __tablename__ = 'organizations'

    oid: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name_boss: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[str] = mapped_column(String(255), nullable=False)
    rank: Mapped[str] = mapped_column(String(255), nullable=False)
    create_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    update_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    department_rel: Mapped[List["Department"]] = relationship("Department", back_populates="organization_rel")
    user_rel: Mapped[List["User"]] = relationship("User", back_populates="organization_rel")


    def __repr__(self) -> str:
        return f"Organization(oid={self.oid!r}, name={self.name!r}, name_boss={self.name_boss!r}, position={self.position!r}, rank={self.rank!r})"