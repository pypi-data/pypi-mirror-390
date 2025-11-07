import uuid
from typing import Optional,TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
if TYPE_CHECKING:
    from healthdatalayer.models import MedicalVisit

class OrganSystemReview(SQLModel, table=True):
    __tablename__ = "organ_system_review"

    organ_system_review_id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)

    medical_visit_id: Optional[uuid.UUID] = Field(default=None, foreign_key="medical_visit.medical_visit_id")
    medical_visit: Optional["MedicalVisit"] = Relationship(back_populates="organ_system_reviews")

    comment:str

    skin_attachment: Optional[bool] = Field(default=None)
    sense_organs: Optional[bool] = Field(default=None)
    breathing: Optional[bool] = Field(default=None)
    cardiovascular: Optional[bool] = Field(default=None)
    digestive: Optional[bool] = Field(default=None)
    genitourinary: Optional[bool] = Field(default=None)
    skeletal_muscle: Optional[bool] = Field(default=None)
    endocrine: Optional[bool] = Field(default=None)
    heme_lifatic: Optional[bool] = Field(default=None)
    nervous: Optional[bool] = Field(default=None)

    is_active: bool = Field(default=True)