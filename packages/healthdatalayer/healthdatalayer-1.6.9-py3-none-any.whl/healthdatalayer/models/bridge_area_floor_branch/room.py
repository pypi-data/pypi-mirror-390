import uuid
from sqlmodel import SQLModel, Field

class Room(SQLModel, table=True):
    __tablename__ = "room"
    
    room_id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)
    name:str