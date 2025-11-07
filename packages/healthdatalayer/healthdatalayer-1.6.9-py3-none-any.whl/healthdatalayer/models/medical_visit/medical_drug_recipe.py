import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

#from healthdatalayer.models import MedicalDrug
if TYPE_CHECKING:
    from healthdatalayer.models import MedicalRecipeVisit,MedicalDrug

class MedicalDrugRecipe(SQLModel, table=True):
    __tablename__ = "medical_drug_recipe"

    medical_drug_recipe_id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)

    medical_drug_id: uuid.UUID = Field(foreign_key="medical_drug.medical_drug_id", primary_key=True)
    medical_drug: Optional["MedicalDrug"] = Relationship()
    medical_recipe_visit_id: uuid.UUID = Field(foreign_key="medical_recipe_visit.medical_recipe_visit_id", primary_key=True)
    medical_recipe_visit: Optional["MedicalRecipeVisit"] = Relationship()
    
    quantity:int
    suplied:bool
    comment:Optional[str] = Field(default=None)
    suplied_date: Optional[datetime] = Field(default=None)

    is_active: bool = Field(default=True)