from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base
from typing import List

class Resource(Base):
    __tablename__ = "resources"
    __table_args__ = (UniqueConstraint("codename", "action"),)
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    codename: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    
    roles: Mapped[List["Role"]] = relationship(secondary="role_resource", back_populates="resources")