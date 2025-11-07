import uuid
from sqlmodel import SQLModel, Field

class Area(SQLModel, table=True):
    __tablename__ = "area"
    
    area_id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)
    name:str