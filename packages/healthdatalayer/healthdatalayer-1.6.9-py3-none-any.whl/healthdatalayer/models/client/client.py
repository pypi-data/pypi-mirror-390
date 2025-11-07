import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .address import Address
    from .gender import Gender

class Client(SQLModel):
    __abstract__ = True
    
    client_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    first_name: str
    birth_date: Optional[datetime] = Field(default=None)
    identification: str
    
    gender_id: Optional[uuid.UUID] = Field(default=None, foreign_key="gender.gender_id")
    address_id: Optional[uuid.UUID] = Field(default=None, foreign_key="address.address_id")
    
    blood_type: Optional[str] = None
    is_active: bool = Field(default=True)

Client.gender = Relationship()
Client.address = Relationship()