from typing import Optional, List
from uuid import UUID
from sqlmodel import select

from healthdatalayer.models import System
from healthdatalayer.config.db import engines, get_session

class SystemRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")
    
    def create_command(self, system: System) -> System:
        with get_session(self.tenant) as session:
            session.add(system)
            session.commit()
            session.refresh(system)
            return system
    
    def get_by_id_command(self, system_id: UUID) -> Optional[System]:
        with get_session(self.tenant) as session:
            return session.get(System, system_id)
    
    def get_by_name_command(self, name: str) -> Optional[System]:
        with get_session(self.tenant) as session:
            statement = select(System).where(System.name == name)
            result = session.exec(statement).first()
            return result
    
    def list_all_command(self, active_only: bool = True) -> List[System]:
        with get_session(self.tenant) as session:
            statement = select(System)
            
            if active_only:
                statement = statement.where(System.is_active == True)
            
            results = session.exec(statement)
            return results.all()
    
    def update_command(self, system_id: UUID, **kwargs) -> Optional[System]:
        with get_session(self.tenant) as session:
            db_system = session.get(System, system_id)
            if not db_system:
                return None
            
            for key, value in kwargs.items():
                if hasattr(db_system, key):
                    setattr(db_system, key, value)
            
            session.add(db_system)
            session.commit()
            session.refresh(db_system)
            return db_system
    
    def delete_command(self, system_id: UUID, soft_delete: bool = True) -> bool:
        with get_session(self.tenant) as session:
            db_system = session.get(System, system_id)
            if not db_system:
                return False
            
            if soft_delete:
                db_system.is_active = False
                session.add(db_system)
            else:
                session.delete(db_system)
            
            session.commit()
            return True