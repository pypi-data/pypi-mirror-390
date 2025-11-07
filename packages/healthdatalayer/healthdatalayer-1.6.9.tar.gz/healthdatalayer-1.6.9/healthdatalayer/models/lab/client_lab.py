import uuid
from sqlmodel import SQLModel,Field,Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from healthdatalayer.models.client.px import Px

class ClientLab(SQLModel,table=True):
    __tablename__ = "client_lab"
    
    client_id: uuid.UUID = Field(foreign_key="px.client_id", primary_key=True)
    client: Optional["Px"] = Relationship()
    medical_lab_id: uuid.UUID = Field(foreign_key="medical_lab.medical_lab_id", primary_key=True)