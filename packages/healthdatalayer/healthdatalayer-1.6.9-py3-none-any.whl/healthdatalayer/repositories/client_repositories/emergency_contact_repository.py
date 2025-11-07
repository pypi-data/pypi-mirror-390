from typing import Optional, List
from uuid import UUID
from sqlmodel import select

from healthdatalayer.models import EmergencyContact
from healthdatalayer.config.db import engines, get_session

class EmergencyContactRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")
        
    def create_command(self, emergency_contact: EmergencyContact) -> EmergencyContact:
        with get_session(self.tenant) as session:
            session.add(emergency_contact)
            session.commit()
            session.refresh(emergency_contact)
            return emergency_contact
    
    def get_by_id_command(self, emergency_contact_id: UUID) -> Optional[EmergencyContact]:
        with get_session(self.tenant) as session:
            return session.get(EmergencyContact, emergency_contact_id)
    
    def get_by_client_id_command(self, client_id: UUID) -> List[EmergencyContact]:
        with get_session(self.tenant) as session:
            statement = select(EmergencyContact).where(
                EmergencyContact.client_id == client_id, 
                EmergencyContact.is_active == True
            )
            results = session.exec(statement)
            return results.all()
    
    def get_by_name_command(self, name: str) -> Optional[EmergencyContact]:
        with get_session(self.tenant) as session:
            statement = select(EmergencyContact).where(EmergencyContact.name == name)
            result = session.exec(statement).first()
            return result
    
    def list_all_command(self, active_only: bool = True) -> List[EmergencyContact]:
        with get_session(self.tenant) as session:
            statement = select(EmergencyContact)
            
            if active_only:
                statement = statement.where(EmergencyContact.is_active == True)
            
            results = session.exec(statement)
            return results.all()
    
    def update_command(self, emergency_contact_id: UUID, **kwargs) -> Optional[EmergencyContact]:
        with get_session(self.tenant) as session:
            db_emergency_contact = session.get(EmergencyContact, emergency_contact_id)
            if not db_emergency_contact:
                return None
            
            for key, value in kwargs.items():
                if hasattr(db_emergency_contact, key):
                    setattr(db_emergency_contact, key, value)
            
            session.add(db_emergency_contact)
            session.commit()
            session.refresh(db_emergency_contact)
            return db_emergency_contact
    
    def delete_command(self, emergency_contact_id: UUID, soft_delete: bool = True) -> bool:
        with get_session(self.tenant) as session:
            db_emergency_contact = session.get(EmergencyContact, emergency_contact_id)
            if not db_emergency_contact:
                return False
            
            if soft_delete:
                db_emergency_contact.is_active = False
                session.add(db_emergency_contact)
            else:
                session.delete(db_emergency_contact)
            
            session.commit()
            return True