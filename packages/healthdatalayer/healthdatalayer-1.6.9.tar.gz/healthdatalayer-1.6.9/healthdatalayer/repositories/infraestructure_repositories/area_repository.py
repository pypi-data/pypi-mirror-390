from typing import Optional, List
from uuid import UUID
from sqlmodel import select

from healthdatalayer.models import Area
from healthdatalayer.config.db import engines, get_session

class AreaRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")
    
    def create_command(self, area: Area) -> Area:
        with get_session(self.tenant) as session:
            session.add(area)
            session.commit()
            session.refresh(area)
            return area
    
    def get_by_id_command(self, area_id: UUID) -> Optional[Area]:
        with get_session(self.tenant) as session:
            return session.get(Area, area_id)
    
    def get_by_name_command(self, name: str) -> Optional[Area]:
        with get_session(self.tenant) as session:
            statement = select(Area).where(Area.name == name)
            result = session.exec(statement).first()
            return result
    
    def list_all_command(self, active_only: bool = True) -> List[Area]:
        with get_session(self.tenant) as session:
            statement = select(Area)
            
            if active_only:
                statement = statement.where(Area.is_active == True)
            
            results = session.exec(statement)
            return results.all()
    
    def update_command(self, area_id: UUID, **kwargs) -> Optional[Area]:
        with get_session(self.tenant) as session:
            db_area = session.get(Area, area_id)
            if not db_area:
                return None
            
            for key, value in kwargs.items():
                if hasattr(db_area, key):
                    setattr(db_area, key, value)
            
            session.add(db_area)
            session.commit()
            session.refresh(db_area)
            return db_area
    
    def delete_command(self, area_id: UUID, soft_delete: bool = True) -> bool:
        with get_session(self.tenant) as session:
            db_area = session.get(Area, area_id)
            if not db_area:
                return False
            
            if soft_delete:
                db_area.is_active = False
                session.add(db_area)
            else:
                session.delete(db_area)
            
            session.commit()
            return True