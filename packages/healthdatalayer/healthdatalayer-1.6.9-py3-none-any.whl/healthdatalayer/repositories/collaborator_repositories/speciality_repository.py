from typing import Optional, List
from uuid import UUID
from sqlmodel import select

from healthdatalayer.models import Speciality
from healthdatalayer.config.db import engines, get_session

class SpecialityRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")
        
    def create_command(self, speciality : Speciality) -> Speciality:
        with get_session(self.tenant) as session:
            session.add(speciality)
            session.commit()
            session.refresh(speciality)
            return speciality
    
    def get_by_id_command(self, speciality_id: UUID) -> Optional[Speciality]:
        with get_session(self.tenant) as session:
            return session.get(Speciality, speciality_id)
    
    def get_by_name_command(self, name: str) -> Optional[Speciality]:
        with get_session(self.tenant) as session:
            statement = select(Speciality).where(Speciality.name == name)
            result = session.exec(statement).first()
            return result
    
    def get_by_subspeciality_command(self, subspeciality: str) -> Optional[List[Speciality]]:
        with get_session(self.tenant) as session:
            statement = select(Speciality).where(Speciality.subspeciality == subspeciality)
            result = session.exec(statement).first()
            return result
    
    def list_all_command(self, active_only: bool = True) -> List[Speciality]:
        with get_session(self.tenant) as session:
            statement = select(Speciality)
            
            if active_only:
                statement = statement.where(Speciality.is_active == True)
            
            results = session.exec(statement)
            return results.all()
    
    def update_command(self, speciality_id: UUID, **kwargs) -> Optional[Speciality]:
        with get_session(self.tenant) as session:
            db_speciality = session.get(Speciality, speciality_id)
            if not db_speciality:
                return None
            
            for key, value in kwargs.items():
                if hasattr(db_speciality, key):
                    setattr(db_speciality, key, value)
            
            session.add(db_speciality)
            session.commit()
            session.refresh(db_speciality)
            return db_speciality
    
    def delete_command(self, speciality_id: UUID, soft_delete: bool = True) -> bool:
        with get_session(self.tenant) as session:
            db_speciality = session.get(Speciality, speciality_id)
            if not db_speciality:
                return False
            
            if soft_delete:
                db_speciality.is_active = False
                session.add(db_speciality)
            else:
                session.delete(db_speciality)
            
            session.commit()
            return True