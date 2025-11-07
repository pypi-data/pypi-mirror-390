import uuid
from sqlmodel import SQLModel,Field

class ClientType(SQLModel,table=True):
    __tablename__ = "client_type"
    
    client_type_id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)
    name:str
    is_active: bool = Field(default=True)