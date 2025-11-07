import uuid
from sqlmodel import SQLModel, Field

class System(SQLModel, table=True):
    __tablename__ = "system"
    
    system_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str