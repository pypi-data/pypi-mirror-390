from typing import Optional, List
from uuid import UUID
from sqlmodel import select, or_

from healthdatalayer.models import MedicalDiagnosis
from healthdatalayer.config.db import engines, get_session

class MedicalDiagnosisRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")
        
    def create_command(self, medical_diagnosis: MedicalDiagnosis) -> MedicalDiagnosis:
        with get_session(self.tenant) as session:
            session.add(medical_diagnosis)
            session.commit()
            session.refresh(medical_diagnosis)
            return medical_diagnosis
    
    def get_by_id_command(self, medical_diagnosis_id: UUID) -> Optional[MedicalDiagnosis]:
        with get_session(self.tenant) as session:
            return session.get(MedicalDiagnosis, medical_diagnosis_id)

    def get_by_name_command(self, name:str, active_only: bool = True) -> Optional[MedicalDiagnosis]:
        with get_session(self.tenant) as session:
            statement = select(MedicalDiagnosis).where(MedicalDiagnosis.name == name)
            
            if active_only:
                statement = statement.where(MedicalDiagnosis.is_active == True)
            
            medical_diagnosis = session.exec(statement).first()
            return medical_diagnosis
    
    def get_by_name_code_ilike_command(self, name:str, active_only: bool = True) -> List[MedicalDiagnosis]:
        with get_session(self.tenant) as session:
            statement = select(MedicalDiagnosis).where(
                or_(
                MedicalDiagnosis.name.ilike(f"%{name}%"), 
                MedicalDiagnosis.cie_10_code.ilike(f"%{name}%")
                )
            )
            
            if active_only:
                statement = statement.where(MedicalDiagnosis.is_active == True)
            
            medical_diagnosis = session.exec(statement).all()
            return medical_diagnosis
    
    def get_by_code_command(self, code:str, active_only: bool = True) -> Optional[MedicalDiagnosis]:
        with get_session(self.tenant) as session:
            statement = select(MedicalDiagnosis).where(MedicalDiagnosis.cie_10_code == code)
            
            if active_only:
                statement = statement.where(MedicalDiagnosis.is_active == True)
            
            medical_diagnosis = session.exec(statement).first()
            return medical_diagnosis
    
    def list_all_command(self, active_only: bool = True) -> List[MedicalDiagnosis]:
        with get_session(self.tenant) as session:
            statement = select(MedicalDiagnosis)
            
            if active_only:
                statement = statement.where(MedicalDiagnosis.is_active == True)
            
            results = session.exec(statement)
            return results.all()
    
    def update_command(self, medical_diagnosis_id: UUID, **kwargs) -> Optional[MedicalDiagnosis]:
        with get_session(self.tenant) as session:
            db_medical_diagnosis = session.get(MedicalDiagnosis, medical_diagnosis_id)
            if not db_medical_diagnosis:
                return None
            
            for key, value in kwargs.items():
                if hasattr(db_medical_diagnosis, key):
                    setattr(db_medical_diagnosis, key, value)
            
            session.add(db_medical_diagnosis)
            session.commit()
            session.refresh(db_medical_diagnosis)
            return db_medical_diagnosis
    
    def delete_command(self, medical_diagnosis_id: UUID, soft_delete: bool = True) -> bool:
        with get_session(self.tenant) as session:
            db_medical_diagnosis = session.get(MedicalDiagnosis, medical_diagnosis_id)
            if not db_medical_diagnosis:
                return False
            
            if soft_delete:
                db_medical_diagnosis.is_active = False
                session.add(db_medical_diagnosis)
            else:
                session.delete(db_medical_diagnosis)
            
            session.commit()
            return True