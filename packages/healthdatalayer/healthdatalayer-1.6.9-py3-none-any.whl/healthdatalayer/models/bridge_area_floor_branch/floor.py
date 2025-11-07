import uuid
from sqlmodel import SQLModel, Field

class Floor(SQLModel, table=True):
    __tablename__ = "floor"
    
    floor_id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)
    name:str