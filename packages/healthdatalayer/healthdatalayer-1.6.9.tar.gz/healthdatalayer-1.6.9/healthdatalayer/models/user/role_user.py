import uuid
from sqlmodel import SQLModel,Field

class RoleUser(SQLModel,table=True):
    __tablename__ = "role_user"
    
    role_id: uuid.UUID = Field(foreign_key="role.role_id", primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.user_id", primary_key=True)