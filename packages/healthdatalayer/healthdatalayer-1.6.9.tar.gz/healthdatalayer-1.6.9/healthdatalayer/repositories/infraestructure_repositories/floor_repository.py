from typing import Optional, List
from uuid import UUID
from sqlmodel import select

from healthdatalayer.models import Floor
from healthdatalayer.config.db import engines, get_session

class FloorRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")
    
    def create_command(self, floor: Floor) -> Floor:
        with get_session(self.tenant) as session:
            session.add(floor)
            session.commit()
            session.refresh(floor)
            return floor
    
    def get_by_id_command(self, floor_id: UUID) -> Optional[Floor]:
        with get_session(self.tenant) as session:
            return session.get(Floor, floor_id)
    
    def get_by_name_command(self, name: str) -> Optional[Floor]:
        with get_session(self.tenant) as session:
            statement = select(Floor).where(Floor.name == name)
            result = session.exec(statement).first()
            return result
    
    def list_all_command(self, active_only: bool = True) -> List[Floor]:
        with get_session(self.tenant) as session:
            statement = select(Floor)
            
            if active_only:
                statement = statement.where(Floor.is_active == True)
            
            results = session.exec(statement)
            return results.all()
    
    def update_command(self, floor_id: UUID, **kwargs) -> Optional[Floor]:
        with get_session(self.tenant) as session:
            db_floor = session.get(Floor, floor_id)
            if not db_floor:
                return None
            
            for key, value in kwargs.items():
                if hasattr(db_floor, key):
                    setattr(db_floor, key, value)
            
            session.add(db_floor)
            session.commit()
            session.refresh(db_floor)
            return db_floor
    
    def delete_command(self, floor_id: UUID, soft_delete: bool = True) -> bool:
        with get_session(self.tenant) as session:
            db_floor = session.get(Floor, floor_id)
            if not db_floor:
                return False
            
            if soft_delete:
                db_floor.is_active = False
                session.add(db_floor)
            else:
                session.delete(db_floor)
            
            session.commit()
            return True