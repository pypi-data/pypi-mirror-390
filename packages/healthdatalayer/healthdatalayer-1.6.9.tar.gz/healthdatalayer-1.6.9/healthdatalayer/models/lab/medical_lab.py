import uuid
from typing import Optional,List,TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from .measure_lab import MeasureLab
if TYPE_CHECKING:
    from .client_lab import ClientLab

class MedicalLab(SQLModel, table=True):
    __tablename__ = "medical_lab"
    
    medical_lab_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    parameter: str
    measure_lab_id: Optional[uuid.UUID] = Field(default=None, foreign_key="measure_lab.measure_lab_id")
    is_active: bool = Field(default=True)
    
MedicalLab.measure_lab = Relationship(back_populates="medical_labs")
MedicalLab.pxs = Relationship(back_populates="medical_labs", link_model="ClientLab")