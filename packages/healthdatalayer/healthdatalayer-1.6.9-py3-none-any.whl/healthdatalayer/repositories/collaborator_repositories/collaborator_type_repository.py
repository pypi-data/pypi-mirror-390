from typing import Optional, List
from uuid import UUID
from sqlmodel import select

from healthdatalayer.models import CollaboratorType
from healthdatalayer.config.db import engines, get_session

class CollaboratorTypeRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")
    
    def create_command(self,collaborator_type : CollaboratorType)-> CollaboratorType:
        with get_session(self.tenant) as session:
            session.add(collaborator_type)
            session.commit()
            session.refresh(collaborator_type)
            return collaborator_type
    
    def get_by_id_command(self, collaborator_type_id: UUID) -> Optional[CollaboratorType]:
        with get_session(self.tenant) as session:
            return session.get(CollaboratorType, collaborator_type_id)
    
    def get_by_name_command(self, name: str) -> Optional[CollaboratorType]:
        with get_session(self.tenant) as session:
            statement = select(CollaboratorType).where(CollaboratorType.name == name)
            result = session.exec(statement).first()
            return result
    
    def list_all_command(self, active_only: bool = True) -> List[CollaboratorType]:
        with get_session(self.tenant) as session:
            statement = select(CollaboratorType)
            
            if active_only:
                statement = statement.where(CollaboratorType.is_active == True)
            
            results = session.exec(statement)
            return results.all()
    
    def update_command(self, collaborator_type_id: UUID, **kwargs) -> Optional[CollaboratorType]:
        with get_session(self.tenant) as session:
            db_collaborator_type = session.get(CollaboratorType, collaborator_type_id)
            if not db_collaborator_type:
                return None
            
            for key, value in kwargs.items():
                if hasattr(db_collaborator_type, key):
                    setattr(db_collaborator_type, key, value)
            
            session.add(db_collaborator_type)
            session.commit()
            session.refresh(db_collaborator_type)
            return db_collaborator_type
    
    def delete_command(self, collaborator_type_id: UUID, soft_delete: bool = True) -> bool:
        with get_session(self.tenant) as session:
            db_collaborator_type = session.get(CollaboratorType, collaborator_type_id)
            if not db_collaborator_type:
                return False
            
            if soft_delete:
                db_collaborator_type.is_active = False
                session.add(db_collaborator_type)
            else:
                session.delete(db_collaborator_type)
            
            session.commit()
            return True