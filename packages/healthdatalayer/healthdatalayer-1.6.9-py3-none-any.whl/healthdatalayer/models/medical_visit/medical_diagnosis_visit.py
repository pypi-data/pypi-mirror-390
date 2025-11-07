import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from healthdatalayer.models import MedicalDiagnosis

if TYPE_CHECKING:
    from healthdatalayer.models import MedicalVisit

class MedicalDiagnosisVisit(SQLModel, table=True):
    __tablename__ = "medical_diagnosis_visit"

    medical_diagnosis_visit_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    diagnosis_date: Optional[datetime] = Field(default=None)
    comments: str
    
    medical_diagnosis_id: Optional[uuid.UUID] = Field(default=None, foreign_key="medical_diagnosis.medical_diagnosis_id")
    medical_diagnosis: Optional[MedicalDiagnosis] = Relationship()
    
    medical_visit_id: Optional[uuid.UUID] = Field(default=None, foreign_key="medical_visit.medical_visit_id")
    medical_visit: Optional["MedicalVisit"] = Relationship(back_populates="medical_diagnosis_visits")
    
    type_diagnosis: str

    is_active: bool = Field(default=True)