import uuid
from sqlmodel import SQLModel, Field, Relationship
from typing import List, TYPE_CHECKING

from healthdatalayer.models.user.role_permission import RolePermission
from healthdatalayer.models.user.permission_user import PermissionUser

if TYPE_CHECKING:
    from healthdatalayer.models.user.user import User
    from healthdatalayer.models.user.role import Role

class Permission(SQLModel, table=True):
    __tablename__ = "permission"

    permission_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    is_active: bool

    roles: List["Role"] = Relationship(
        back_populates="permissions",
        link_model=RolePermission
    )

    users: List["User"] = Relationship(
        back_populates="permissions",
        link_model=PermissionUser
    )