import uuid
from sqlmodel import SQLModel,Field

class MarriageStatus(SQLModel,table=True):
    __tablename__ = "marriage_status"
    
    marriage_status_id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)
    name:str
    is_active: bool = Field(default=True)