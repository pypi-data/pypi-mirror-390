import uuid
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

from healthdatalayer.models import User
from healthdatalayer.models import CollaboratorSpeciality


if TYPE_CHECKING:
    from healthdatalayer.models import Speciality
    from healthdatalayer.models import CollaboratorType
    

class Collaborator(SQLModel, table=True):
    __tablename__ = "collaborator"
    
    collaborator_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    ruc: str
    code: str
    
    collaborator_type_id: Optional[uuid.UUID] = Field(default=None, foreign_key="collaborator_type.collaborator_type_id")
    collaborator_type: Optional["CollaboratorType"] = Relationship()
    
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.user_id")
    user: Optional[User] = Relationship()

    is_active: bool = Field(default=True)
    
    specialties: List["Speciality"] = Relationship(
        back_populates="collaborators",
        link_model=CollaboratorSpeciality
    )