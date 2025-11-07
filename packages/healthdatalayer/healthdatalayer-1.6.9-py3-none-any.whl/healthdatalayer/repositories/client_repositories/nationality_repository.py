from typing import Optional, List
from uuid import UUID
from sqlmodel import select

from healthdatalayer.models import Nationality
from healthdatalayer.config.db import engines, get_session

class NationalityRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")
    
    def create_command(self, nationality: Nationality) -> Nationality:
        with get_session(self.tenant) as session:
            session.add(nationality)
            session.commit()
            session.refresh(nationality)
            return nationality
    
    def get_by_id_command(self, nationality_id: UUID) -> Optional[Nationality]:
        with get_session(self.tenant) as session:
            return session.get(Nationality, nationality_id)
    
    def get_by_name_command(self, name: str) -> Optional[Nationality]:
        with get_session(self.tenant) as session:
            statement = select(Nationality).where(Nationality.name.ilike(f"%{name}%"), Nationality.is_active == True)
            result = session.exec(statement).first()
            return result
    
    def list_all_command(self, active_only: bool = True) -> List[Nationality]:
        with get_session(self.tenant) as session:
            statement = select(Nationality)
            
            if active_only:
                statement = statement.where(Nationality.is_active == True)
            
            results = session.exec(statement)
            return results.all()
    
    def update_command(self, nationality_id: UUID, **kwargs) -> Optional[Nationality]:
        with get_session(self.tenant) as session:
            db_nationality = session.get(Nationality, nationality_id)
            if not db_nationality:
                return None
            
            for key, value in kwargs.items():
                if hasattr(db_nationality, key):
                    setattr(db_nationality, key, value)
            
            session.add(db_nationality)
            session.commit()
            session.refresh(db_nationality)
            return db_nationality
    
    def delete_command(self, nationality_id: UUID, soft_delete: bool = True) -> bool:
        with get_session(self.tenant) as session:
            db_nationality = session.get(Nationality, nationality_id)
            if not db_nationality:
                return False
            
            if soft_delete:
                db_nationality.is_active = False
                session.add(db_nationality)
            else:
                session.delete(db_nationality)
            
            session.commit()
            return True