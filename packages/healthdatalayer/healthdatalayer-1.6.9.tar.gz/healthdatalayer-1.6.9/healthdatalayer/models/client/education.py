import uuid
from sqlmodel import SQLModel,Field

class Education(SQLModel,table=True):
    __tablename__ = "education"
    
    education_id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)
    name:str
    is_active: bool = Field(default=True)