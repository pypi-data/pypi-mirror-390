import uuid
from sqlmodel import SQLModel,Field

class Nationality(SQLModel,table=True):
    __tablename__ = "nationality"
    
    nationality_id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)
    name:str
    code:str
    is_active: bool = Field(default=True)