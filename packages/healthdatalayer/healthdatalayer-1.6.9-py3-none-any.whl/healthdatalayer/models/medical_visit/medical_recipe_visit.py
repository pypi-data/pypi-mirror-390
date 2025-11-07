import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship


from healthdatalayer.models import MedicalDrugRecipe

if TYPE_CHECKING:
    from healthdatalayer.models.medical_visit.medical_drug import MedicalDrug
    from healthdatalayer.models import MedicalVisit

class MedicalRecipeVisit(SQLModel, table=True):
    __tablename__ = "medical_recipe_visit"
    
    medical_recipe_visit_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    completed_supplied: bool
    completed_supplied_date: Optional[datetime] = Field(default=None)
    
    medical_visit_id: Optional[uuid.UUID] = Field(default=None, foreign_key="medical_visit.medical_visit_id")
    medical_visit: Optional["MedicalVisit"] = Relationship(back_populates="medical_recipe_visits")

    is_active: bool = Field(default=True)
    
    medical_drug_recipes: List["MedicalDrugRecipe"] = Relationship(
        back_populates="medical_recipe_visit",
        sa_relationship_kwargs={"lazy": "selectin"}
    )