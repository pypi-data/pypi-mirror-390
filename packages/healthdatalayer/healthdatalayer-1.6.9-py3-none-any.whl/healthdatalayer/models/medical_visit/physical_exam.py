import uuid
from typing import Optional,TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from healthdatalayer.models import MedicalVisit

class PhysicalExam(SQLModel, table=True):
    __tablename__ = "physical_exam"

    physical_exam_id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)

    medical_visit_id: Optional[uuid.UUID] = Field(default=None, foreign_key="medical_visit.medical_visit_id")
    medical_visit: Optional["MedicalVisit"] = Relationship(back_populates="physical_exams")

    comments: Optional[str] = Field(default=None)
    
    r1: Optional[bool] = Field(default=None)
    r2: Optional[bool] = Field(default=None)
    r3: Optional[bool] = Field(default=None)
    r4: Optional[bool] = Field(default=None)
    r5: Optional[bool] = Field(default=None)
    r6: Optional[bool] = Field(default=None)
    r7: Optional[bool] = Field(default=None)
    r8: Optional[bool] = Field(default=None)
    r9: Optional[bool] = Field(default=None)
    r10: Optional[bool] = Field(default=None)
    r11: Optional[bool] = Field(default=None)
    r12: Optional[bool] = Field(default=None)
    r13: Optional[bool] = Field(default=None)
    r14: Optional[bool] = Field(default=None)
    r15: Optional[bool] = Field(default=None)

    s1: Optional[bool] = Field(default=None)
    s2: Optional[bool] = Field(default=None)
    s3: Optional[bool] = Field(default=None)
    s4: Optional[bool] = Field(default=None)
    s5: Optional[bool] = Field(default=None)
    s6: Optional[bool] = Field(default=None)
    s7: Optional[bool] = Field(default=None)
    s8: Optional[bool] = Field(default=None)
    s9: Optional[bool] = Field(default=None)
    s10: Optional[bool] = Field(default=None)

    is_active: bool = Field(default=True)