import uuid
from sqlmodel import SQLModel,Field, Relationship
from typing import Optional

from healthdatalayer.models.client.px import Px

class EmergencyContact(SQLModel,table=True):
    __tablename__ = "emergency_contact"
    
    emergency_contact_id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)

    client_id:Optional[uuid.UUID]=Field(default=None,foreign_key="px.client_id")
    client: Optional[Px] = Relationship()

    name:str
    phone:str
    is_active: bool = Field(default=True)