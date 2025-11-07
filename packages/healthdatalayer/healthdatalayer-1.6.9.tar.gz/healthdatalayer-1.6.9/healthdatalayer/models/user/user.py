import uuid
from sqlmodel import SQLModel,Field, Relationship
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from healthdatalayer.models.user.role_user import RoleUser
from healthdatalayer.models.user.permission_user import PermissionUser

from healthdatalayer.models.user.role import Role
from healthdatalayer.models.user.permission import Permission
    
class User(SQLModel,table=True):
    __tablename__ = "user"

    user_id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)
    username: str = Field(index=True, nullable=False, unique=True)
    password: str = Field(nullable=False)
    last_access: Optional[datetime] = Field(default=None)
    email: Optional[str] = None
    is_active: bool 

    roles: List["Role"] = Relationship(
        back_populates="users",
        link_model=RoleUser
    )

    permissions: List["Permission"] = Relationship(
        back_populates="users",
        link_model=PermissionUser
    )