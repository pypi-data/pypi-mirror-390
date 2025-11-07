from typing import Optional, List
from uuid import UUID
from sqlmodel import select

from healthdatalayer.models import ClientType
from healthdatalayer.config.db import engines, get_session

class ClientTypeRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")
    
    def create_command(self, client_type: ClientType) -> ClientType:
        with get_session(self.tenant) as session:
            session.add(client_type)
            session.commit()
            session.refresh(client_type)
            return client_type
    
    def get_by_id_command(self, client_type_id: UUID) -> Optional[ClientType]:
        with get_session(self.tenant) as session:
            return session.get(ClientType, client_type_id)
    
    def get_by_name_command(self, name: str) -> Optional[ClientType]:
        with get_session(self.tenant) as session:
            statement = select(ClientType).where(ClientType.name == name)
            result = session.exec(statement).first()
            return result
    
    def list_all_command(self, active_only: bool = True) -> List[ClientType]:
        with get_session(self.tenant) as session:
            statement = select(ClientType)
            
            if active_only:
                statement = statement.where(ClientType.is_active == True)
            
            results = session.exec(statement)
            return results.all()
    
    def update_command(self, client_type_id: UUID, **kwargs) -> Optional[ClientType]:
        with get_session(self.tenant) as session:
            db_client_type = session.get(ClientType, client_type_id)
            if not db_client_type:
                return None
            
            for key, value in kwargs.items():
                if hasattr(db_client_type, key):
                    setattr(db_client_type, key, value)
            
            session.add(db_client_type)
            session.commit()
            session.refresh(db_client_type)
            return db_client_type
    
    def delete_command(self, client_type_id: UUID, soft_delete: bool = True) -> bool:
        with get_session(self.tenant) as session:
            db_client_type = session.get(ClientType, client_type_id)
            if not db_client_type:
                return False
            
            if soft_delete:
                db_client_type.is_active = False
                session.add(db_client_type)
            else:
                session.delete(db_client_type)
            
            session.commit()
            return True