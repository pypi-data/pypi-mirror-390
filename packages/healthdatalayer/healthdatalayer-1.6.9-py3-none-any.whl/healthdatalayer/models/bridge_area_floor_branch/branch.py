import uuid
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

from healthdatalayer.models import System

class Branch(SQLModel, table=True):
    __tablename__ = "branch"
    
    branch_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    location_x: Optional[float] = None
    location_y: Optional[float] = None
    
    system_id: Optional[uuid.UUID] = Field(default=None, foreign_key="system.system_id")
    system: Optional[System] = Relationship()