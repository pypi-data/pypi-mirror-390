from typing import Optional, List
from uuid import UUID
from sqlmodel import select

from healthdatalayer.models import Address, City, State
from healthdatalayer.config.db import engines, get_session

class AddressRepository:
    
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")
    
    def create_command(self, address: Address) -> Address:
        with get_session(self.tenant) as session:
            session.add(address)
            session.commit()
            session.refresh(address)
            return address
    
    def get_by_id_command(self, address_id: UUID) -> Optional[Address]:
        with get_session(self.tenant) as session:
            return session.get(Address, address_id)
    
    def list_all_command(self, active_only: bool = True) -> List[Address]:
        with get_session(self.tenant) as session:
            statement = select(Address)
            
            if active_only:
                statement = statement.where(Address.is_active == True)
            
            results = session.exec(statement)
            return results.all()
    
    def update_command(self, address_id: UUID, **kwargs) -> Optional[Address]:
        with get_session(self.tenant) as session:
            db_address = session.get(Address, address_id)
            if not db_address:
                return None
            
            for key, value in kwargs.items():
                if hasattr(db_address, key):
                    setattr(db_address, key, value)
            
            session.add(db_address)
            session.commit()
            session.refresh(db_address)
            return db_address
    
    def delete_command(self, address_id: UUID, soft_delete: bool = True) -> bool:
        with get_session(self.tenant) as session:
            db_address = session.get(Address, address_id)
            if not db_address:
                return False
            
            if soft_delete:
                db_address.is_active = False
                session.add(db_address)
            else:
                session.delete(db_address)
            
            session.commit()
            return True
        
    def list_all_state_command(self, active_only: bool = True) -> List[Address]:
        with get_session(self.tenant) as session:
            statement = select(State)
            
            if active_only:
                statement = statement.where(State.is_active == True)
            
            results = session.exec(statement)
            return results.all()
    
    def list_all_city_command(self, active_only: bool = True) -> List[Address]:
        with get_session(self.tenant) as session:
            statement = select(City)
            
            if active_only:
                statement = statement.where(City.is_active == True)
            
            results = session.exec(statement)
            return results.all()
    
    def list_city_by_state_id_command(self,state_id: UUID, active_only: bool = True) -> List[Address]:
        with get_session(self.tenant) as session:
            statement = select(City).where(City.state_id == state_id)
            
            if active_only:
                statement = statement.where(State.is_active == True)
            
            results = session.exec(statement)
            return results.all()