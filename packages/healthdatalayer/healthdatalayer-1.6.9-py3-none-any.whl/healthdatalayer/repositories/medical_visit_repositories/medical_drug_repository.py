from typing import Optional, List
from uuid import UUID
from sqlmodel import select,or_

from healthdatalayer.models import MedicalDrug
from healthdatalayer.config.db import engines, get_session

class MedicalDrugRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")
        
    def create_command(self, medical_drug: MedicalDrug) -> MedicalDrug:
        with get_session(self.tenant) as session:
            session.add(medical_drug)
            session.commit()
            session.refresh(medical_drug)
            return medical_drug
        
    def get_by_id_command(self, medical_drug_id: UUID) -> Optional[MedicalDrug]:
        with get_session(self.tenant) as session:
            return session.get(MedicalDrug, medical_drug_id)
    
    def list_all_command(self, active_only: bool = True) -> List[MedicalDrug]:
        with get_session(self.tenant) as session:
            statement = select(MedicalDrug)
            
            if active_only:
                statement = statement.where(MedicalDrug.is_active == True)
            
            results = session.exec(statement)
            return results.all()
    
    def update_command(self, medical_drug_id: UUID, **kwargs) -> Optional[MedicalDrug]:
        with get_session(self.tenant) as session:
            db_medical_drug = session.get(MedicalDrug, medical_drug_id)
            if not db_medical_drug:
                return None
            
            for key, value in kwargs.items():
                if hasattr(db_medical_drug, key):
                    setattr(db_medical_drug, key, value)
            
            session.add(db_medical_drug)
            session.commit()
            session.refresh(db_medical_drug)
            return db_medical_drug
    
    def delete_command(self, medical_drug_id: UUID, soft_delete: bool = True) -> bool:
        with get_session(self.tenant) as session:
            db_medical_drug = session.get(MedicalDrug, medical_drug_id)
            if not db_medical_drug:
                return False
            
            if soft_delete:
                db_medical_drug.is_active = False
                session.add(db_medical_drug)
            else:
                session.delete(db_medical_drug)
            
            session.commit()
            return True
    
    def get_by_name_code_ilike_command(self, name:str, active_only: bool = True) -> List[MedicalDrug]:
        with get_session(self.tenant) as session:
            statement = select(MedicalDrug).where(
                or_(
                MedicalDrug.drug_name.ilike(f"%{name}%"), 
                MedicalDrug.drug_code.ilike(f"%{name}%")
                )
            )
            
            if active_only:
                statement = statement.where(MedicalDrug.is_active == True)
            
            medical_diagnosis = session.exec(statement).all()
            return medical_diagnosis