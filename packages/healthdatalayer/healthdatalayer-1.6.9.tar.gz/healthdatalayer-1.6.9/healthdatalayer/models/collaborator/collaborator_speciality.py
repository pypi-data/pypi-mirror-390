import uuid
from sqlmodel import SQLModel,Field

class CollaboratorSpeciality(SQLModel,table=True):
    __tablename__ = "collaborator_speciality"
    
    speciality_id: uuid.UUID = Field(foreign_key="speciality.speciality_id", primary_key=True)
    collaborator_id: uuid.UUID = Field(foreign_key="collaborator.collaborator_id", primary_key=True)