from typing import Optional, List
from uuid import UUID
from sqlmodel import select

from healthdatalayer.models import Room
from healthdatalayer.config.db import engines, get_session

class RoomRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")
    
    def create_command(self, room: Room) -> Room:
        with get_session(self.tenant) as session:
            session.add(room)
            session.commit()
            session.refresh(room)
            return room
    
    def get_by_id_command(self, room_id: UUID) -> Optional[Room]:
        with get_session(self.tenant) as session:
            return session.get(Room, room_id)
    
    def get_by_name_command(self, name: str) -> Optional[Room]:
        with get_session(self.tenant) as session:
            statement = select(Room).where(Room.name == name)
            result = session.exec(statement).first()
            return result
    
    def list_all_command(self, active_only: bool = True) -> List[Room]:
        with get_session(self.tenant) as session:
            statement = select(Room)
            
            if active_only:
                statement = statement.where(Room.is_active == True)
            
            results = session.exec(statement)
            return results.all()
    
    def update_command(self, room_id: UUID, **kwargs) -> Optional[Room]:
        with get_session(self.tenant) as session:
            db_room = session.get(Room, room_id)
            if not db_room:
                return None
            
            for key, value in kwargs.items():
                if hasattr(db_room, key):
                    setattr(db_room, key, value)
            
            session.add(db_room)
            session.commit()
            session.refresh(db_room)
            return db_room
    
    def delete_command(self, room_id: UUID, soft_delete: bool = True) -> bool:
        with get_session(self.tenant) as session:
            db_room = session.get(Room, room_id)
            if not db_room:
                return False
            
            if soft_delete:
                db_room.is_active = False
                session.add(db_room)
            else:
                session.delete(db_room)
            
            session.commit()
            return True