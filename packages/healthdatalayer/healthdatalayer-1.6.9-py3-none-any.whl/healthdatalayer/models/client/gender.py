import uuid
from sqlmodel import SQLModel,Field

class Gender(SQLModel,table=True):
    __tablename__ = "gender"
    
    gender_id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)
    name:str
    is_active: bool = Field(default=True)