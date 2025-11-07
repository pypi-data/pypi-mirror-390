import uuid
from sqlmodel import SQLModel,Field
from typing import List, TYPE_CHECKING
from sqlmodel import Relationship

from .collaborator_speciality import CollaboratorSpeciality

if TYPE_CHECKING:
    from .collaborator import Collaborator

class Speciality(SQLModel,table=True):
    __tablename__ = "speciality"

    speciality_id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)
    subspeciality:str
    name:str

    is_active: bool = Field(default=True)

    collaborators: List["Collaborator"] = Relationship(
        back_populates="specialties", 
        link_model=CollaboratorSpeciality
    )