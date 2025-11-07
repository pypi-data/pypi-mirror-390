from typing import Optional, List
from uuid import UUID
from sqlmodel import select

from healthdatalayer.models import Gender
from healthdatalayer.config.db import engines, get_session

class GenderRepository:
    
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")
    
    def create_command(self, gender: Gender) -> Gender:
        with get_session(self.tenant) as session:
            session.add(gender)
            session.commit()
            session.refresh(gender)
            return gender
    
    def get_by_id_command(self, gender_id: UUID) -> Optional[Gender]:
        with get_session(self.tenant) as session:
            return session.get(Gender, gender_id)
    
    def get_by_name_command(self, name: str) -> Optional[Gender]:
        with get_session(self.tenant) as session:
            statement = select(Gender).where(Gender.name == name)
            result = session.exec(statement).first()
            return result
    
    def list_all_command(self, active_only: bool = True) -> List[Gender]:
        with get_session(self.tenant) as session:
            statement = select(Gender)
            
            if active_only:
                statement = statement.where(Gender.is_active == True)
            
            results = session.exec(statement)
            return results.all()
    
    def update_command(self, gender_id: UUID, **kwargs) -> Optional[Gender]:
        with get_session(self.tenant) as session:
            db_gender = session.get(Gender, gender_id)
            if not db_gender:
                return None
            
            for key, value in kwargs.items():
                if hasattr(db_gender, key):
                    setattr(db_gender, key, value)
            
            session.add(db_gender)
            session.commit()
            session.refresh(db_gender)
            return db_gender
    
    def delete_command(self, gender_id: UUID, soft_delete: bool = True) -> bool:
        with get_session(self.tenant) as session:
            db_gender = session.get(Gender, gender_id)
            if not db_gender:
                return False
            
            if soft_delete:
                db_gender.is_active = False
                session.add(db_gender)
            else:
                session.delete(db_gender)
            
            session.commit()
            return True