import uuid
from sqlmodel import SQLModel, Field

class MedicalDiagnosis(SQLModel, table=True):
    __tablename__ = "medical_diagnosis"

    medical_diagnosis_id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)

    name:str
    cie_10_code: str = Field(index=True, max_length=10)

    is_active: bool = Field(default=True)