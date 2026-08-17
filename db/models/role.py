from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base
from typing import List

class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    codename: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    
    users: Mapped[List["User"]] = relationship(secondary="user_role", back_populates="roles")
    resources: Mapped[List["Resource"]] = relationship(secondary="role_resource", back_populates="roles")