from typing import Optional, List
from uuid import UUID
from sqlmodel import select

from healthdatalayer.models import Profession
from healthdatalayer.config.db import engines, get_session

class ProfessionRepository:
    
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")
    
    def create_command(self, profession: Profession) -> Profession:
        with get_session(self.tenant) as session:
            session.add(profession)
            session.commit()
            session.refresh(profession)
            return profession
    
    def get_by_id_command(self, profession_id: UUID) -> Optional[Profession]:
        with get_session(self.tenant) as session:
            return session.get(Profession, profession_id)
    
    def get_by_name_command(self, name: str) -> Optional[Profession]:
        with get_session(self.tenant) as session:
            statement = select(Profession).where(Profession.name == name)
            result = session.exec(statement).first()
            return result
    
    def list_all_command(self, active_only: bool = True) -> List[Profession]:
        with get_session(self.tenant) as session:
            statement = select(Profession)
            
            if active_only:
                statement = statement.where(Profession.is_active == True)
            
            results = session.exec(statement)
            return results.all()
    
    def update_command(self, profession_id: UUID, **kwargs) -> Optional[Profession]:
        with get_session(self.tenant) as session:
            db_profession = session.get(Profession, profession_id)
            if not db_profession:
                return None
            
            for key, value in kwargs.items():
                if hasattr(db_profession, key):
                    setattr(db_profession, key, value)
            
            session.add(db_profession)
            session.commit()
            session.refresh(db_profession)
            return db_profession
    
    def delete_command(self, profession_id: UUID, soft_delete: bool = True) -> bool:
        with get_session(self.tenant) as session:
            db_profession = session.get(Profession, profession_id)
            if not db_profession:
                return False
            
            if soft_delete:
                db_profession.is_active = False
                session.add(db_profession)
            else:
                session.delete(db_profession)
            
            session.commit()
            return True