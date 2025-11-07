from typing import Optional, List
from uuid import UUID
from sqlmodel import select, or_
from sqlalchemy.orm import selectinload,joinedload
from healthdatalayer.models import PhysicalExam
from healthdatalayer.models import MedicalVisit
from healthdatalayer.config.db import engines, get_session

class PhysicalExamRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")
    
    def create_command(self, physical_exam: PhysicalExam) -> PhysicalExam:
        with get_session(self.tenant) as session:
            session.add(physical_exam)
            session.commit()
            session.refresh(physical_exam)
            return physical_exam
    
    def get_by_id_command(self, physical_exam_id: UUID, load_relations: bool = False) -> Optional[PhysicalExam]:
        with get_session(self.tenant) as session:
            
            if load_relations:
                statement = select(PhysicalExam).where(PhysicalExam.physical_exam_id == physical_exam_id).options(
                    joinedload(PhysicalExam.medical_visit)
                )
                physical_exam = session.exec(statement).first()
               
                return physical_exam
            else:
                return session.get(PhysicalExam, physical_exam_id)
    
    def get_by_medical_visit_id_command(self, medical_visit_id: UUID, load_relations: bool = False) ->Optional[PhysicalExam]:
        with get_session(self.tenant) as session:
            
            statement = select(PhysicalExam).where(PhysicalExam.medical_visit_id == medical_visit_id)
            if load_relations:
                statement = statement.options(
                    joinedload(PhysicalExam.medical_visit)
                )
            physical_exam = session.exec(statement).first()
            
            return physical_exam 
    
    def get_all_command(self, active_only: bool = True,load_related: bool = False) -> List[PhysicalExam]:
        with get_session(self.tenant) as session:
            
            statement = select(PhysicalExam)
            
            if load_related:
                statement = select(PhysicalExam).options(
                    selectinload(PhysicalExam.medical_visit)
                )
            
            if active_only:
                statement = statement.where(PhysicalExam.is_active == True)
                physical_exam = session.exec(statement).all()
                
            return physical_exam
        
    def update_command(self, physical_exam: PhysicalExam) -> PhysicalExam:
        with get_session(self.tenant) as session:
            existing_physical_exam = session.get(PhysicalExam, physical_exam.physical_exam_id)
            if not existing_physical_exam:
                raise ValueError(f"triage with id {physical_exam.physical_exam_id} does not exist")
            
            for key, value in physical_exam.dict(exclude_unset=True).items():
                setattr(existing_physical_exam, key, value)
            
            bd_physical_exam =  session.merge(existing_physical_exam)
            session.commit()
            session.refresh(bd_physical_exam)
            return bd_physical_exam
        
    def delete_command(self, physical_exam_id: UUID, soft_delete: bool = False)->None:
        with get_session(self.tenant) as session:
            existing_physical_exam = session.get(PhysicalExam, physical_exam_id)
            if not existing_physical_exam:
                raise ValueError(f"MedicalVisit with id {physical_exam_id} does not exist")

            if soft_delete:
                existing_physical_exam.is_active = False
                session.add(existing_physical_exam)
            else:
                session.delete(existing_physical_exam)

            session.commit()