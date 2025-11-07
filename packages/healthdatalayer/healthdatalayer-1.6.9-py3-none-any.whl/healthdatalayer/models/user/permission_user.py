import uuid
from sqlmodel import SQLModel,Field

class PermissionUser(SQLModel,table=True):
    __tablename__ = "permission_user"
    
    permission_id: uuid.UUID = Field(foreign_key="permission.permission_id", primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.user_id", primary_key=True)