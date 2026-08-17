from sqlalchemy import Table, Column, Integer, ForeignKey
from db.base import Base

user_role = Table(
    "user_role",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
)

role_resource = Table(
    "role_resource",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("resource_id", Integer, ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True)
)