import uuid
from typing import Optional,TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from decimal import Decimal

if TYPE_CHECKING:
    from healthdatalayer.models.medical_visit.medical_visit import MedicalVisit

class VisitTriage(SQLModel, table=True):
    __tablename__ = "visit_triage"

    visit_triage_id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)
    
    weight:Optional[Decimal]=Field(default=None)
    height:Optional[Decimal]=Field(default=None)
    heart_rate:Optional[int]=Field(default=None)
    blood_pressure:Optional[str]=Field(default=None)
    temperature:Optional[Decimal]=Field(default=None)

    imc:Optional[Decimal]=Field(default=None)
    abdominal_perimeter:Optional[Decimal]=Field(default=None)
    capillary_hemoglobin:Optional[Decimal]=Field(default=None)
    pulse_oximetry:Optional[Decimal]=Field(default=None)
    
    medical_visit_id:Optional[uuid.UUID]=Field(default=None,foreign_key="medical_visit.medical_visit_id")
    medical_visit: Optional["MedicalVisit"] = Relationship()

    is_active: bool = Field(default=True)