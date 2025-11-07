from typing import Optional, List
from uuid import UUID
from sqlmodel import select

from healthdatalayer.models import Education
from healthdatalayer.config.db import engines, get_session

class EducationRepository:
    
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")
    
    def create_command(self, education: Education) -> Education:
        with get_session(self.tenant) as session:
            session.add(education)
            session.commit()
            session.refresh(education)
            return education
    
    def get_by_id_command(self, education_id: UUID) -> Optional[Education]:
        with get_session(self.tenant) as session:
            return session.get(Education, education_id)
    
    def get_by_name_command(self, name: str) -> Optional[Education]:
        with get_session(self.tenant) as session:
            statement = select(Education).where(Education.name == name)
            result = session.exec(statement).first()
            return result
    
    def list_all_command(self, active_only: bool = True) -> List[Education]:
        with get_session(self.tenant) as session:
            statement = select(Education)
            
            if active_only:
                statement = statement.where(Education.is_active == True)
            
            results = session.exec(statement)
            return results.all()
    
    def update_command(self, education_id: UUID, **kwargs) -> Optional[Education]:
        with get_session(self.tenant) as session:
            db_education = session.get(Education, education_id)
            if not db_education:
                return None
            
            for key, value in kwargs.items():
                if hasattr(db_education, key):
                    setattr(db_education, key, value)
            
            session.add(db_education)
            session.commit()
            session.refresh(db_education)
            return db_education
    
    def delete_command(self, education_id: UUID, soft_delete: bool = True) -> bool:
        with get_session(self.tenant) as session:
            db_education = session.get(Education, education_id)
            if not db_education:
                return False
            
            if soft_delete:
                db_education.is_active = False
                session.add(db_education)
            else:
                session.delete(db_education)
            
            session.commit()
            return True