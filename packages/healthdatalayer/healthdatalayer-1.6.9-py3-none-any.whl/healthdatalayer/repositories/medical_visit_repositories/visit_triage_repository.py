from typing import Optional, List
from uuid import UUID
from sqlmodel import select
from sqlalchemy.orm import selectinload,joinedload
from healthdatalayer.models import VisitTriage
from healthdatalayer.models import MedicalVisit
from healthdatalayer.config.db import engines, get_session

class VisitTriageRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")
        
    def create_command(self, visit_triage: VisitTriage) -> VisitTriage:
        with get_session(self.tenant) as session:
            session.add(visit_triage)
            session.commit()
            session.refresh(visit_triage)
            return visit_triage

    def get_by_id_command(self, visit_triage_id: UUID, load_relations: bool = False) -> Optional[VisitTriage]:
        with get_session(self.tenant) as session:
            
            if load_relations:
                statement = select(VisitTriage).where(VisitTriage.visit_triage_id == visit_triage_id).options(
                    joinedload(VisitTriage.medical_visit)
                )
                visit_triage = session.exec(statement).first()
               
                return visit_triage
            else:
                return session.get(VisitTriage, visit_triage_id)
    
    def get_by_medical_visit_id_command(self, medical_visit_id: UUID, load_relations: bool = False) ->Optional[VisitTriage]:
        with get_session(self.tenant) as session:
            
            statement = select(VisitTriage).where(VisitTriage.medical_visit_id == medical_visit_id)
            if load_relations:
                statement = statement.options(
                    joinedload(VisitTriage.medical_visit)
                )
            visit_triage = session.exec(statement).first()
            
            return visit_triage 
    
    def get_all_command(self, active_only: bool = True,load_related: bool = False) -> List[VisitTriage]:
        with get_session(self.tenant) as session:
            
            statement = select(VisitTriage)
            
            if load_related:
                statement = select(VisitTriage).options(
                    selectinload(VisitTriage.medical_visit)
                )
            
            if active_only:
                statement = statement.where(VisitTriage.is_active == True)
                visit_triage = session.exec(statement).all()
                
            return visit_triage
        
    def update_command(self, visit_triage: VisitTriage) -> VisitTriage:
        with get_session(self.tenant) as session:
            existing_visit_triage = session.get(VisitTriage, visit_triage.visit_triage_id)
            if not existing_visit_triage:
                raise ValueError(f"triage with id {visit_triage.visit_triage_id} does not exist")
            
            for key, value in visit_triage.dict(exclude_unset=True).items():
                setattr(existing_visit_triage, key, value)
            
            bd_visit_triage =  session.merge(existing_visit_triage)
            session.commit()
            session.refresh(bd_visit_triage)
            return bd_visit_triage
        
    def delete_command(self, visit_triage_id: UUID, soft_delete: bool = False)->None:
        with get_session(self.tenant) as session:
            existing_visit_triage = session.get(MedicalVisit, visit_triage_id)
            if not existing_visit_triage:
                raise ValueError(f"MedicalVisit with id {visit_triage_id} does not exist")

            if soft_delete:
                existing_visit_triage.is_active = False
                session.add(existing_visit_triage)
            else:
                session.delete(existing_visit_triage)

            session.commit()

    def exists_by_medical_visit_id_command(self, medical_visit_id: UUID) -> bool:
        with get_session(self.tenant) as session:
            statement = select(VisitTriage).where(VisitTriage.medical_visit_id == medical_visit_id)
            result = session.exec(statement).first()
            return result is not None