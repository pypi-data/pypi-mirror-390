import uuid
from sqlmodel import SQLModel, Field, Relationship
from typing import List, TYPE_CHECKING

from healthdatalayer.models.user.role_user import RoleUser
from healthdatalayer.models.user.role_permission import RolePermission

if TYPE_CHECKING:
    from healthdatalayer.models.user.user import User
    from healthdatalayer.models.user.permission import Permission

class Role(SQLModel, table=True):
    __tablename__ = "role"

    role_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    is_active: bool

    users: List["User"] = Relationship(
        back_populates="roles",
        link_model=RoleUser
    )

    permissions: List["Permission"] = Relationship(
        back_populates="roles",
        link_model=RolePermission
    )