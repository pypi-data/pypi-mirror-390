from typing import Optional, List
from uuid import UUID
from sqlmodel import select

from healthdatalayer.models import MarriageStatus
from healthdatalayer.config.db import engines, get_session

class MarriageStatusRepository:
    
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")
    
    def create_command(self, marriage_status: MarriageStatus) -> MarriageStatus:
        with get_session(self.tenant) as session:
            session.add(marriage_status)
            session.commit()
            session.refresh(marriage_status)
            return marriage_status
    
    def get_by_id_command(self, marriage_status_id: UUID) -> Optional[MarriageStatus]:
        with get_session(self.tenant) as session:
            return session.get(MarriageStatus, marriage_status_id)
    
    def get_by_name_command(self, name: str) -> Optional[MarriageStatus]:
        with get_session(self.tenant) as session:
            statement = select(MarriageStatus).where(MarriageStatus.name == name)
            result = session.exec(statement).first()
            return result
    
    def list_all_command(self, active_only: bool = True) -> List[MarriageStatus]:
        with get_session(self.tenant) as session:
            statement = select(MarriageStatus)
            
            if active_only:
                statement = statement.where(MarriageStatus.is_active == True)
            
            results = session.exec(statement)
            return results.all()
    
    def update_command(self, marriage_status_id: UUID, **kwargs) -> Optional[MarriageStatus]:
        with get_session(self.tenant) as session:
            db_marriage_status = session.get(MarriageStatus, marriage_status_id)
            if not db_marriage_status:
                return None
            
            for key, value in kwargs.items():
                if hasattr(db_marriage_status, key):
                    setattr(db_marriage_status, key, value)
            
            session.add(db_marriage_status)
            session.commit()
            session.refresh(db_marriage_status)
            return db_marriage_status
    
    def delete_command(self, marriage_status_id: UUID, soft_delete: bool = True) -> bool:
        with get_session(self.tenant) as session:
            db_marriage_status = session.get(MarriageStatus, marriage_status_id)
            if not db_marriage_status:
                return False
            
            if soft_delete:
                db_marriage_status.is_active = False
                session.add(db_marriage_status)
            else:
                session.delete(db_marriage_status)
            
            session.commit()
            return True