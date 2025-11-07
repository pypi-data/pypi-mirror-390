from typing import Optional, TYPE_CHECKING, List
from sqlmodel import Field, Relationship
import uuid

from healthdatalayer.models import Client


if TYPE_CHECKING:
    from healthdatalayer.models import ClientLab
    from healthdatalayer.models import PathologicalHistory
    

class Px(Client, table=True):
    __tablename__ = "px"
    
    last_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    medical_record_number: Optional[str] = None
    marriage_status_id: Optional[uuid.UUID] = Field(default=None, foreign_key="marriage_status.marriage_status_id")
    profession_id: Optional[uuid.UUID] = Field(default=None, foreign_key="profession.profession_id")
    education_id: Optional[uuid.UUID] = Field(default=None, foreign_key="education.education_id")
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.user_id")
    nationality_id: Optional[uuid.UUID] = Field(default=None, foreign_key="nationality.nationality_id")
    pathological_histories: List["PathologicalHistory"] = Relationship(
        back_populates="client",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

Px.marriage_status = Relationship()
Px.profession = Relationship()
Px.education = Relationship()
Px.user = Relationship()
Px.nationality = Relationship()
Px.medical_labs = Relationship(back_populates="pxs", link_model="ClientLab")
