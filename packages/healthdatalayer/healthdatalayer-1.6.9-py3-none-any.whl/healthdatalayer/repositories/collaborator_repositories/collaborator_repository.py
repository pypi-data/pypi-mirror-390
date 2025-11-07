from datetime import date
from typing import Optional, List
from uuid import UUID
from sqlmodel import select, or_, join, text
from sqlalchemy.orm import selectinload,joinedload
from healthdatalayer.models import Collaborator
from healthdatalayer.models import Speciality, CollaboratorSpeciality
from healthdatalayer.dtos import ScheduleCollaboratorDTO
from healthdatalayer.config.db import engines, get_session

class CollaboratorRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")
        
    def create_command(self, collaborator: Collaborator) -> Collaborator:
        with get_session(self.tenant) as session:
            session.add(collaborator)
            session.commit()
            session.refresh(collaborator)
            return collaborator
        
    def get_by_id_command(self, collaborator_id: UUID, load_relations: bool = False) -> Optional[Collaborator]:
        with get_session(self.tenant) as session:
            if load_relations:
                statement = select(Collaborator).where(Collaborator.collaborator_id == collaborator_id).options(
                    selectinload(Collaborator.collaborator_type),
                    joinedload(Collaborator.user),
                    selectinload(Collaborator.specialties) 
                )
                collaborator = session.exec(statement).first()
                        
                return collaborator
            else:
                return session.get(Collaborator, collaborator_id)
            
    def get_by_speciality_id_command(self, speciality_id: UUID, load_relations: bool = False) -> List[Collaborator]:
        with get_session(self.tenant) as session:
            statement = (
                select(Collaborator)
                .join(CollaboratorSpeciality)
                .where(CollaboratorSpeciality.speciality_id == speciality_id, Collaborator.is_active == True)
            )
            
            if load_relations:
                statement = statement.options(
                    selectinload(Collaborator.collaborator_type),
                    joinedload(Collaborator.user),
                    selectinload(Collaborator.specialties)    
                )
                
            collaborators = session.exec(statement).all()
                        
            return collaborators
    
    def get_by_ruc_name_code_command(self, content: str, active_only: bool = True, load_relations : bool = False)->List[Collaborator]:
        with get_session(self.tenant) as session:
            
            query = select(Collaborator).where(
                    or_(
                        Collaborator.name.ilike(f"%{content}%"),
                        Collaborator.ruc.ilike(f"%{content}%"),
                        Collaborator.code.ilike(f"%{content}%")
                    )
                )
            
            if load_relations:
                query = select(Collaborator).options(
                    selectinload(Collaborator.collaborator_type),
                    joinedload(Collaborator.user),
                    selectinload(Collaborator.specialties)
                ).where(
                    or_(
                        Collaborator.name.ilike(f"%{content}%"),
                        Collaborator.ruc.ilike(f"%{content}%"),
                        Collaborator.code.ilike(f"%{content}%")
                    )
                )

            if active_only:
                query.where(Collaborator.is_active == True)
                
            collaborators = session.exec(query).all()
            
            return collaborators
                
            
    def get_all_command(self, active_only: bool = True,load_related: bool = False) -> List[Collaborator]:
        with get_session(self.tenant) as session:
            
            statement = select(Collaborator)
            
            if load_related:
                
                statement = statement.options(
                    selectinload(Collaborator.collaborator_type),
                    joinedload(Collaborator.user),
                    selectinload(Collaborator.specialties) 
                )         
            
            if active_only:
                statement = statement.where(Collaborator.is_active == True)
                
            return session.exec(statement).all()
    
    def update_command(self, collaborator: Collaborator) -> Collaborator:
        with get_session(self.tenant) as session:
            existing_collaborator = session.get(Collaborator, collaborator.collaborator_id)
            if not existing_collaborator:
                raise ValueError(f"collaborator with id {collaborator.collaborator_id} does not exist")
            
            for key, value in collaborator.dict(exclude_unset=True).items():
                setattr(existing_collaborator, key, value)
            
            bd_collaborator =  session.merge(existing_collaborator)
            session.commit()
            session.refresh(bd_collaborator)
            return bd_collaborator
        
    def delete_command(self, collaborator_id: UUID, soft_delete: bool = False)->None:
        with get_session(self.tenant) as session:
            existing_bridge = session.get(Collaborator, collaborator_id)
            if not existing_bridge:
                raise ValueError(f"Collaborator with id {collaborator_id} does not exist")

            if soft_delete:
                existing_bridge.is_active = False
                session.add(existing_bridge)
            else:
                session.delete(existing_bridge)

            session.commit()
    
    def assign_speciality_command(self, collaborator_id: UUID, speciality_id: UUID) -> Optional[Collaborator]:
        with get_session(self.tenant) as session:
            collab_statement = select(Collaborator).options(selectinload(Collaborator.specialties)).where(Collaborator.collaborator_id == collaborator_id)
            collab = session.exec(collab_statement).first()
            if not collab:
                return None
            
            speciality = session.get(Speciality, speciality_id)
            if not speciality:
                return None
            
            if speciality not in collab.specialties:
                collab.specialties.append(speciality)
                session.add(collab)
                session.commit()
                session.refresh(collab)
            
            return collab
    
    def get_availability_schedules_command(self, visit_date: date, collaborator_id: str) -> ScheduleCollaboratorDTO:
    
        with get_session(self.tenant) as session:
            
            query = text("""
                WITH horarios_generados AS (
                    SELECT horario::TIME as hora
                    FROM generate_series(
                        CAST(:fecha AS DATE)+ TIME '08:00:00',
                        CAST(:fecha AS DATE) + TIME '17:00:00',
                        INTERVAL '30 minutes'
                    ) AS horario
                ),
                horarios_ocupados AS (
                    SELECT t.visit_date::TIME as hora
                    FROM medical_visit t
                    WHERE t.visit_date::DATE = :fecha
                    AND t.collaborator_id = :colab_id
                    AND t.status_visit in ('AGENDADO','REAGENDADO')
                )
                SELECT 
                    hg.hora,
                    CASE WHEN ho.hora IS NOT NULL THEN true ELSE false END as ocupado
                FROM horarios_generados hg
                LEFT JOIN horarios_ocupados ho ON hg.hora = ho.hora
                ORDER BY hg.hora
            """)
            
            result = session.exec(query, params={"fecha": visit_date, "colab_id": collaborator_id})
            
            availables = []
            busy = []
            
            for row in result.fetchall():
                hour, is_busy = row[0], row[1]
                if is_busy:
                    busy.append(hour)
                else:
                    availables.append(hour)
            
            return ScheduleCollaboratorDTO(
                available_schedules=availables,
                busy_schedules=busy
            )