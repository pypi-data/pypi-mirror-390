import uuid
from sqlmodel import SQLModel,Field

class RolePermission(SQLModel,table=True):
    __tablename__ = "role_permission"
    
    role_id: uuid.UUID = Field(foreign_key="role.role_id", primary_key=True)
    permission_id: uuid.UUID = Field(foreign_key="permission.permission_id", primary_key=True)