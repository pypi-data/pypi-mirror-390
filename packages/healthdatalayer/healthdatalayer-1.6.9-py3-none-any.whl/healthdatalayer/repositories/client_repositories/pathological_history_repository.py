from typing import Optional, List
from uuid import UUID
from sqlmodel import select

from healthdatalayer.models import PathologicalHistory
from healthdatalayer.config.db import engines, get_session

class PathologicalHistoryRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")
        
    def create_command(self, pathological_history: PathologicalHistory) -> PathologicalHistory:
        with get_session(self.tenant) as session:
            session.add(pathological_history)
            session.commit()
            session.refresh(pathological_history)
            return pathological_history
    
    def get_by_id_command(self, pathological_history_id: UUID) -> Optional[PathologicalHistory]:
        with get_session(self.tenant) as session:
            return session.get(PathologicalHistory, pathological_history_id)
    
    def get_by_client_id_command(self, client_id: UUID) -> List[PathologicalHistory]:
        with get_session(self.tenant) as session:
            statement = select(PathologicalHistory).where(
                PathologicalHistory.client_id == client_id, 
                PathologicalHistory.is_active == True
            )
            results = session.exec(statement)
            return results.all()
    
    
    def list_all_command(self, active_only: bool = True) -> List[PathologicalHistory]:
        with get_session(self.tenant) as session:
            statement = select(PathologicalHistory)
            
            if active_only:
                statement = statement.where(PathologicalHistory.is_active == True)
            
            results = session.exec(statement)
            return results.all()
    
    def update_command(self, pathological_history_id: UUID, **kwargs) -> Optional[PathologicalHistory]:
        with get_session(self.tenant) as session:
            db_pathological_history = session.get(PathologicalHistory, pathological_history_id)
            if not db_pathological_history:
                return None
            
            for key, value in kwargs.items():
                if hasattr(db_pathological_history, key):
                    setattr(db_pathological_history, key, value)
            
            session.add(db_pathological_history)
            session.commit()
            session.refresh(db_pathological_history)
            return db_pathological_history
    
    def delete_command(self, pathological_history_id: UUID, soft_delete: bool = True) -> bool:
        with get_session(self.tenant) as session:
            db_pathological_history = session.get(PathologicalHistory, pathological_history_id)
            if not db_pathological_history:
                return False
            
            if soft_delete:
                db_pathological_history.is_active = False
                session.add(db_pathological_history)
            else:
                session.delete(db_pathological_history)
            
            session.commit()
            return True