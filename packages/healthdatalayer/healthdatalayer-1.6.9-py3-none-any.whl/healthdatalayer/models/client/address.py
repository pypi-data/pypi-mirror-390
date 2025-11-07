import uuid
from sqlmodel import SQLModel,Field

class Address(SQLModel,table=True):
    __tablename__ = "address"
    
    address_id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)
    postal_code:str = Field(default=None)
    state:str
    country:str
    city:str
    neighborhood:str
    is_active: bool = Field(default=True)