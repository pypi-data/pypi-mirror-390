import uuid
from sqlmodel import SQLModel,Field

class Profession(SQLModel,table=True):
    __tablename__ = "profession"
    
    profession_id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)
    name:str
    is_active: bool = Field(default=True)