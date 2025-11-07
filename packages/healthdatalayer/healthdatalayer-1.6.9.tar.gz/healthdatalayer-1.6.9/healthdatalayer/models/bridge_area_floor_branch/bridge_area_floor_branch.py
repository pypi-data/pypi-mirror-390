import uuid
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

from .area import Area
from .branch import Branch
from .floor import Floor
from .room import Room

class BridgeAreaFloorBranch(SQLModel, table=True):
    __tablename__ = "bridge_area_floor_branch"
    
    bridge_area_floor_branch_id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)

    area_id:Optional[uuid.UUID]=Field(default=None,foreign_key="area.area_id")
    area: Optional[Area] = Relationship()

    branch_id:Optional[uuid.UUID]=Field(default=None,foreign_key="branch.branch_id")
    branch: Optional[Branch] = Relationship()

    floor_id:Optional[uuid.UUID]=Field(default=None,foreign_key="floor.floor_id")
    floor: Optional[Floor] = Relationship()

    room_id:Optional[uuid.UUID]=Field(default=None,foreign_key="room.room_id")
    room: Optional[Room] = Relationship()

    is_active: bool = Field(default=True)
