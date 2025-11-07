import uuid
from sqlmodel import SQLModel, Field, Relationship

class MeasureLab(SQLModel, table=True):
    __tablename__ = "measure_lab"
    
    measure_lab_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    is_active: bool = Field(default=True)

MeasureLab.medical_labs = Relationship(back_populates="measure_lab")