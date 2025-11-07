import uuid
from sqlmodel import SQLModel,Field,Relationship
from typing import Optional

from healthdatalayer.models.client.px import Px

class PathologicalHistory(SQLModel,table=True):
    __tablename__ = "pathological_history"
    
    pathological_history_id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)

    client_id:Optional[uuid.UUID]=Field(default=None,foreign_key="px.client_id")
    client: Optional[Px] = Relationship()

    type_name:str

    heart_disease: Optional[bool] = Field(default=None)
    hypertension: Optional[bool] = Field(default=None)
    cardiovascular_disease: Optional[bool] = Field(default=None)
    endocrine_metabolic: Optional[bool] = Field(default=None)
    cancer: Optional[bool] = Field(default=None)
    tuberculosis: Optional[bool] = Field(default=None)
    mental_illness: Optional[bool] = Field(default=None)
    malformation: Optional[bool] = Field(default=None)
    other: Optional[bool] = Field(default=None)

    comment:str

    is_active: bool = Field(default=True)