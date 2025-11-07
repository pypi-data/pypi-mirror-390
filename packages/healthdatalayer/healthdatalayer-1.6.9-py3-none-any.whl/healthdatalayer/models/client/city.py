import uuid
from sqlmodel import SQLModel,Field
from typing import Optional

class City(SQLModel,table=True):
    __tablename__ = "city"
    
    city_id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)
    name:str
    state_id: Optional[uuid.UUID] = Field(default=None, foreign_key="state.state_id")
    is_active: bool = Field(default=True)