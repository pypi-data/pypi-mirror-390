from typing import Optional, List
from uuid import UUID
from sqlmodel import select, or_
from sqlalchemy.orm import selectinload,joinedload
from healthdatalayer.models import MedicalDiagnosisVisit
from healthdatalayer.models import MedicalVisit
from healthdatalayer.config.db import engines, get_session

class MedicalDiagnosisVisitRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")
    
    def create_command(self, medical_diagnosis_visit: MedicalDiagnosisVisit) -> MedicalDiagnosisVisit:
        with get_session(self.tenant) as session:
            session.add(medical_diagnosis_visit)
            session.commit()
            session.refresh(medical_diagnosis_visit)
            return medical_diagnosis_visit
    
    def get_by_id_command(self, medical_diagnosis_visit_id: UUID, load_relations: bool = False) -> Optional[MedicalDiagnosisVisit]:
        with get_session(self.tenant) as session:
            
            if load_relations:
                statement = select(MedicalDiagnosisVisit).where(MedicalDiagnosisVisit.medical_diagnosis_visit_id == medical_diagnosis_visit_id).options(
                    joinedload(MedicalDiagnosisVisit.medical_visit),
                    joinedload(MedicalDiagnosisVisit.medical_diagnosis)
                )
                medical_diagnosis_visit = session.exec(statement).first()
               
                return medical_diagnosis_visit
            else:
                return session.get(MedicalDiagnosisVisit, medical_diagnosis_visit_id)
    
    def get_by_medical_visit_id_command(self, medical_visit_id: UUID, load_relations: bool = False) ->List[MedicalDiagnosisVisit]:
        with get_session(self.tenant) as session:
            
            statement = select(MedicalDiagnosisVisit).where(MedicalDiagnosisVisit.medical_visit_id == medical_visit_id)
            if load_relations:
                statement = statement.options(
                    joinedload(MedicalDiagnosisVisit.medical_visit),
                    joinedload(MedicalDiagnosisVisit.medical_diagnosis)
                )
            medical_diagnosis_visits = session.exec(statement).all()
            
            return medical_diagnosis_visits
    
    def get_by_medicalvisitid_and_diagnosisid_command(self, medical_visit_id: UUID, medical_diagnosis_id: UUID, load_relations: bool = False) ->Optional[MedicalDiagnosisVisit]:
        with get_session(self.tenant) as session:
            
            statement = select(MedicalDiagnosisVisit).where(
                MedicalDiagnosisVisit.medical_visit_id == medical_visit_id,
                MedicalDiagnosisVisit.medical_diagnosis_id == medical_diagnosis_id
            )

            if load_relations:
                statement = statement.options(
                    joinedload(MedicalDiagnosisVisit.medical_visit),
                    joinedload(MedicalDiagnosisVisit.medical_diagnosis)
                )
            medical_diagnosis_visit = session.exec(statement).first()
            
            return medical_diagnosis_visit
    
    def list_all_command(self, active_only: bool = True,load_related: bool = False) -> List[MedicalDiagnosisVisit]:
        with get_session(self.tenant) as session:
            
            statement = select(MedicalDiagnosisVisit)
            
            if load_related:
                statement = select(MedicalDiagnosisVisit).options(
                    selectinload(MedicalDiagnosisVisit.medical_visit),
                    joinedload(MedicalDiagnosisVisit.medical_diagnosis)
                )
            
            if active_only:
                statement = statement.where(MedicalDiagnosisVisit.is_active == True)
                medical_diagnosis_visit = session.exec(statement).all()
                
            return medical_diagnosis_visit
        
    def update_command(self, medical_diagnosis_visit: MedicalDiagnosisVisit) -> MedicalDiagnosisVisit:
        with get_session(self.tenant) as session:
            existing_medical_diagnosis_visit = session.get(MedicalDiagnosisVisit, medical_diagnosis_visit.medical_diagnosis_visit_id)
            if not existing_medical_diagnosis_visit:
                raise ValueError(f"MedicalDiagnosisVisit with id {medical_diagnosis_visit.medical_diagnosis_visit_id} does not exist")
            
            for key, value in medical_diagnosis_visit.dict(exclude_unset=True).items():
                setattr(existing_medical_diagnosis_visit, key, value)
            
            bd_medical_diagnosis_visit =  session.merge(existing_medical_diagnosis_visit)
            session.commit()
            session.refresh(bd_medical_diagnosis_visit)
            return bd_medical_diagnosis_visit
        
    def delete_command(self, medical_diagnosis_visit_id: UUID, soft_delete: bool = False)->None:
        with get_session(self.tenant) as session:
            existing_medical_diagnosis_visit = session.get(MedicalDiagnosisVisit, medical_diagnosis_visit_id)
            if not existing_medical_diagnosis_visit:
                raise ValueError(f"MedicalDiagnosisVisit with id {medical_diagnosis_visit_id} does not exist")

            if soft_delete:
                existing_medical_diagnosis_visit.is_active = False
                session.add(existing_medical_diagnosis_visit)
            else:
                session.delete(existing_medical_diagnosis_visit)

            session.commit() 