from typing import Optional, List
from uuid import UUID
from sqlmodel import select
from sqlalchemy.orm import selectinload

from healthdatalayer.models import Pet
from healthdatalayer.config.db import engines, get_session

class PetRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")

    def create_command(self, pet: Pet) -> Pet:
        with get_session(self.tenant) as session:
            session.add(pet)
            session.commit()
            session.refresh(pet)
            return pet

    def get_by_id_command(self, pet_id: UUID, load_relations: bool = False) -> Optional[Pet]:
        with get_session(self.tenant) as session:
            if load_relations:
                statement = (
                    select(Pet)
                    .where(Pet.client_id == pet_id)
                    .options(
                        selectinload(Pet.gender),
                        selectinload(Pet.address),
                        selectinload(Pet.marriage_status),
                        selectinload(Pet.profession),
                        selectinload(Pet.education),
                        selectinload(Pet.user),
                    )
                )
                result = session.exec(statement).first()
                return result
            else:
                return session.get(Pet, pet_id)
            
    def get_by_identification_command(self, identification: str, load_relations: bool = False) -> Optional[Pet]:
        with get_session(self.tenant) as session:
            statement = select(Pet).where(Pet.identification == identification)
            
            if load_relations:
                statement = statement.options(
                    selectinload(Pet.gender),
                    selectinload(Pet.address),
                    selectinload(Pet.marriage_status),
                    selectinload(Pet.profession),
                    selectinload(Pet.education),
                    selectinload(Pet.user),
                )
            
            result = session.exec(statement).first()
            return result
            
    def search_by_name_command(self, name: str, load_relations: bool = False) -> List[Pet]:
        with get_session(self.tenant) as session:
            statement = select(Pet).where(
                (Pet.first_name.ilike(f"%{name}%")) | 
                (Pet.last_name.ilike(f"%{name}%"))
            )
            
            if load_relations:
                statement = statement.options(
                    selectinload(Pet.gender),
                    selectinload(Pet.address),
                    selectinload(Pet.marriage_status),
                    selectinload(Pet.profession),
                    selectinload(Pet.education),
                    selectinload(Pet.user),
                )
            
            results = session.exec(statement)
            return results.all()
    
    def list_all_command(self, active_only: bool = True, load_relations: bool = False) -> List[Pet]:
        with get_session(self.tenant) as session:
            statement = select(Pet)
            
            if active_only:
                statement = statement.where(Pet.is_active == True)
            
            if load_relations:
                statement = statement.options(
                    selectinload(Pet.gender),
                    selectinload(Pet.address),
                    selectinload(Pet.marriage_status),
                    selectinload(Pet.profession),
                    selectinload(Pet.education),
                )
            
            results = session.exec(statement)
            return results.all()
            
    def update_command(self, pet: Pet) -> Pet:
        with get_session(self.tenant) as session:
            db_pet = session.merge(pet)
            session.commit()
            session.refresh(db_pet)
            return db_pet

    def delete_command(self, pet_id: UUID, soft_delete: bool = True) -> bool:
        with get_session(self.tenant) as session:
            db_pet = session.get(Pet, pet_id)
            if not db_pet:
                return False
            
            if soft_delete:
                db_pet.is_active = False
                session.add(db_pet)
            else:
                session.delete(db_pet)
            
            session.commit()
            return True
    
    def count_command(self, active_only: bool = True) -> int:
        with get_session(self.tenant) as session:
            statement = select(Pet)
            if active_only:
                statement = statement.where(Pet.is_active == True)
            results = session.exec(statement)
            return len(results.all())