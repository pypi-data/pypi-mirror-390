import uuid
from sqlmodel import SQLModel,Field

class CollaboratorType(SQLModel,table=True):
    __tablename__ = "collaborator_type"
    
    collaborator_type_id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)
    name:str
    is_active: bool = Field(default=True)