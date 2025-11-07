import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Enum as SqlEnum

from healthdatalayer.models import Collaborator
from healthdatalayer.models.medical_visit.status_visit_enum import StatusVisitEnum
from healthdatalayer.models import Speciality
from healthdatalayer.models import BridgeAreaFloorBranch 
if TYPE_CHECKING:
    from healthdatalayer.models import Px
    from healthdatalayer.models import MedicalDiagnosisVisit
    from healthdatalayer.models import MedicalRecipeVisit
    from healthdatalayer.models import OrganSystemReview
    from healthdatalayer.models import PhysicalExam
class MedicalVisit(SQLModel, table=True):
    __tablename__ = "medical_visit"

    medical_visit_id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)
    visit_date: Optional[datetime] = Field(default=None)

    collaborator_id:Optional[uuid.UUID]=Field(default=None,foreign_key="collaborator.collaborator_id")
    collaborator: Optional[Collaborator] = Relationship()

    client_id:Optional[uuid.UUID]=Field(default=None,foreign_key="px.client_id")
    client: Optional["Px"] = Relationship()

    speciality_id:Optional[uuid.UUID]=Field(default=None,foreign_key="speciality.speciality_id")
    speciality: Optional[Speciality] = Relationship()

    status_visit: StatusVisitEnum = Field(sa_column=Column(SqlEnum(StatusVisitEnum, native_enum=False), nullable=False))

    next_followup_visit_id:Optional[uuid.UUID]=Field(default=None,foreign_key="medical_visit.medical_visit_id")

    overall_diagnosis:Optional[str]=Field(default=None)

    bridge_area_floor_branch_id:Optional[uuid.UUID]=Field(default=None,foreign_key="bridge_area_floor_branch.bridge_area_floor_branch_id")
    bridge_area_floor_branch: Optional[BridgeAreaFloorBranch] = Relationship()

    reason_visit:Optional[str]=Field(default=None)
    current_illness: Optional[str]=Field(default=None)
    rest: Optional[bool] = Field(default=None)
    rest_hours: Optional[int] = Field(default=None)
    rest_date_start: Optional[datetime] = Field(default=None)
    rest_date_end: Optional[datetime] = Field(default=None)

    is_active: bool = Field(default=True)
    
    medical_diagnosis_visits: List["MedicalDiagnosisVisit"] = Relationship(back_populates="medical_visit")
    medical_recipe_visits: List["MedicalRecipeVisit"] = Relationship(back_populates="medical_visit")
    organ_system_reviews: List["OrganSystemReview"] = Relationship(back_populates="medical_visit")
    physical_exams: List["PhysicalExam"] = Relationship(back_populates="medical_visit")