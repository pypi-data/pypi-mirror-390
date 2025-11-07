from typing import Optional, List
from uuid import UUID
from sqlmodel import select, or_
from sqlalchemy.orm import selectinload,joinedload
from healthdatalayer.models import OrganSystemReview
from healthdatalayer.models import MedicalVisit
from healthdatalayer.config.db import engines, get_session

class OrganSystemReviewRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")
    
    def create_command(self, organ_system_review: OrganSystemReview) -> OrganSystemReview:
        with get_session(self.tenant) as session:
            session.add(organ_system_review)
            session.commit()
            session.refresh(organ_system_review)
            return organ_system_review
    
    def get_by_id_command(self, organ_system_review_id: UUID, load_relations: bool = False) -> Optional[OrganSystemReview]:
        with get_session(self.tenant) as session:
            
            if load_relations:
                statement = select(OrganSystemReview).where(OrganSystemReview.organ_system_review_id == organ_system_review_id).options(
                    joinedload(OrganSystemReview.medical_visit)
                )
                organ_system_review = session.exec(statement).first()
               
                return organ_system_review
            else:
                return session.get(OrganSystemReview, organ_system_review_id)
    
    def get_by_medical_visit_id_command(self, medical_visit_id: UUID, load_relations: bool = False) ->Optional[OrganSystemReview]:
        with get_session(self.tenant) as session:
            
            statement = select(OrganSystemReview).where(OrganSystemReview.medical_visit_id == medical_visit_id)
            if load_relations:
                statement = statement.options(
                    joinedload(OrganSystemReview.medical_visit)
                )
            organ_system_review = session.exec(statement).first()
            
            return organ_system_review 
    
    def get_all_command(self, active_only: bool = True,load_related: bool = False) -> List[OrganSystemReview]:
        with get_session(self.tenant) as session:
            
            statement = select(OrganSystemReview)
            
            if load_related:
                statement = select(OrganSystemReview).options(
                    selectinload(OrganSystemReview.medical_visit)
                )
            
            if active_only:
                statement = statement.where(OrganSystemReview.is_active == True)
                organ_system_review = session.exec(statement).all()
                
            return organ_system_review
        
    def update_command(self, organ_system_review: OrganSystemReview) -> OrganSystemReview:
        with get_session(self.tenant) as session:
            existing_organ_system_review = session.get(OrganSystemReview, organ_system_review.organ_system_review_id)
            if not existing_organ_system_review:
                raise ValueError(f"triage with id {organ_system_review.organ_system_review_id} does not exist")
            
            for key, value in organ_system_review.dict(exclude_unset=True).items():
                setattr(existing_organ_system_review, key, value)
            
            bd_organ_system_review =  session.merge(existing_organ_system_review)
            session.commit()
            session.refresh(bd_organ_system_review)
            return bd_organ_system_review
        
    def delete_command(self, organ_system_review_id: UUID, soft_delete: bool = False)->None:
        with get_session(self.tenant) as session:
            existing_organ_system_review = session.get(OrganSystemReview, organ_system_review_id)
            if not existing_organ_system_review:
                raise ValueError(f"MedicalVisit with id {organ_system_review_id} does not exist")

            if soft_delete:
                existing_organ_system_review.is_active = False
                session.add(existing_organ_system_review)
            else:
                session.delete(existing_organ_system_review)

            session.commit()