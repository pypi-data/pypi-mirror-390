from typing import Optional, List
from uuid import UUID
from sqlmodel import select

from healthdatalayer.models import Px
from healthdatalayer.config.db import engines, get_session

class PxRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")

    def create_command(self, px: Px) -> Px:
        with get_session(self.tenant) as session:
            session.add(px)
            session.commit()
            session.refresh(px)
            return px

    def get_by_id_command(self, px_id: UUID, load_relations: bool = False) -> Optional[Px]:
        with get_session(self.tenant) as session:
            px = session.get(Px, px_id)
            
            if px and load_relations:
                if px.gender_id:
                    from healthdatalayer.models.client.gender import Gender
                    gender_obj = session.get(Gender, px.gender_id)
                    object.__setattr__(px, 'gender', gender_obj)
                
                if px.address_id:
                    from healthdatalayer.models.client.address import Address
                    address_obj = session.get(Address, px.address_id)
                    object.__setattr__(px, 'address', address_obj)
                
                if px.marriage_status_id:
                    from healthdatalayer.models.client.marriage_status import MarriageStatus
                    marriage_status_obj = session.get(MarriageStatus, px.marriage_status_id)
                    object.__setattr__(px, 'marriage_status', marriage_status_obj)
                
                if px.profession_id:
                    from healthdatalayer.models.client.profession import Profession
                    profession_obj = session.get(Profession, px.profession_id)
                    object.__setattr__(px, 'profession', profession_obj)
                
                if px.education_id:
                    from healthdatalayer.models.client.education import Education
                    education_obj = session.get(Education, px.education_id)
                    object.__setattr__(px, 'education', education_obj)
                
                if px.user_id:
                    from healthdatalayer.models.user.user import User
                    user_obj = session.get(User, px.user_id)
                    object.__setattr__(px, 'user', user_obj)
                    
                if px.nationality_id:
                    from healthdatalayer.models.client.nationality import Nationality
                    user_obj = session.get(Nationality, px.nationality_id)
                    object.__setattr__(px, 'nationality', user_obj)
                    
                from healthdatalayer.models.client.pathological_history import PathologicalHistory
                statement = select(PathologicalHistory).where(PathologicalHistory.client_id == px_id)
                pathological_his = session.exec(statement).all()
                if pathological_his:
                    object.__setattr__(px, 'pathological_histories',pathological_his)
            
            return px
            
    def get_by_identification_command(self, identification: str, load_relations: bool = False) -> Optional[Px]:
        with get_session(self.tenant) as session:
            statement = select(Px).where(Px.identification == identification)
            px = session.exec(statement).first()
            
            if px and load_relations:
                if px.gender_id:
                    from healthdatalayer.models.client.gender import Gender
                    gender_obj = session.get(Gender, px.gender_id)
                    object.__setattr__(px, 'gender', gender_obj)
                
                if px.address_id:
                    from healthdatalayer.models.client.address import Address
                    address_obj = session.get(Address, px.address_id)
                    object.__setattr__(px, 'address', address_obj)
                
                if px.marriage_status_id:
                    from healthdatalayer.models.client.marriage_status import MarriageStatus
                    marriage_status_obj = session.get(MarriageStatus, px.marriage_status_id)
                    object.__setattr__(px, 'marriage_status', marriage_status_obj)
                
                if px.profession_id:
                    from healthdatalayer.models.client.profession import Profession
                    profession_obj = session.get(Profession, px.profession_id)
                    object.__setattr__(px, 'profession', profession_obj)
                
                if px.education_id:
                    from healthdatalayer.models.client.education import Education
                    education_obj = session.get(Education, px.education_id)
                    object.__setattr__(px, 'education', education_obj)
                
                if px.user_id:
                    from healthdatalayer.models.user.user import User
                    user_obj = session.get(User, px.user_id)
                    object.__setattr__(px, 'user', user_obj)
                    
                if px.nationality_id:
                    from healthdatalayer.models.client.nationality import Nationality
                    user_obj = session.get(Nationality, px.nationality_id)
                    object.__setattr__(px, 'nationality', user_obj)
                
                    
                from healthdatalayer.models.client.pathological_history import PathologicalHistory
                statement = select(PathologicalHistory).where(PathologicalHistory.client_id == px.client_id)
                pathological_his = session.exec(statement).all()
                if pathological_his:
                    object.__setattr__(px, 'pathological_histories',pathological_his)
            
            
            return px
            
    def search_by_name_command(self, name: str, load_relations: bool = False) -> List[Px]:
        with get_session(self.tenant) as session:
            statement = select(Px).where(
                (Px.first_name.ilike(f"%{name}%")) | 
                (Px.last_name.ilike(f"%{name}%")) |
                (Px.identification.ilike(f"%{name}%"))
            )
            
            results = session.exec(statement).all()
            
            if load_relations:
                for px in results:
                    if px.gender_id:
                        from healthdatalayer.models.client.gender import Gender
                        gender_obj = session.get(Gender, px.gender_id)
                        object.__setattr__(px, 'gender', gender_obj)
                    
                    if px.address_id:
                        from healthdatalayer.models.client.address import Address
                        address_obj = session.get(Address, px.address_id)
                        object.__setattr__(px, 'address', address_obj)
                    
                    if px.marriage_status_id:
                        from healthdatalayer.models.client.marriage_status import MarriageStatus
                        marriage_status_obj = session.get(MarriageStatus, px.marriage_status_id)
                        object.__setattr__(px, 'marriage_status', marriage_status_obj)
                    
                    if px.profession_id:
                        from healthdatalayer.models.client.profession import Profession
                        profession_obj = session.get(Profession, px.profession_id)
                        object.__setattr__(px, 'profession', profession_obj)
                    
                    if px.education_id:
                        from healthdatalayer.models.client.education import Education
                        education_obj = session.get(Education, px.education_id)
                        object.__setattr__(px, 'education', education_obj)
                    
                    if px.user_id:
                        from healthdatalayer.models.user.user import User
                        user_obj = session.get(User, px.user_id)
                        object.__setattr__(px, 'user', user_obj)
                    if px.nationality_id:
                        from healthdatalayer.models.client.nationality import Nationality
                        user_obj = session.get(Nationality, px.nationality_id)
                        object.__setattr__(px, 'nationality', user_obj)
                    
                    from healthdatalayer.models.client.pathological_history import PathologicalHistory
                    statement = select(PathologicalHistory).where(PathologicalHistory.client_id == px.client_id)
                    pathological_his = session.exec(statement).all()
                    if pathological_his:
                        object.__setattr__(px, 'pathological_histories',pathological_his)
                
                
            return results
    
    def list_all_command(self, active_only: bool = True, load_relations: bool = False) -> List[Px]:
        with get_session(self.tenant) as session:
            statement = select(Px)
            
            if active_only:
                statement = statement.where(Px.is_active == True)
            
            results = session.exec(statement).all()
            
            if load_relations:
                for px in results:
                    if px.gender_id:
                        from healthdatalayer.models.client.gender import Gender
                        gender_obj = session.get(Gender, px.gender_id)
                        object.__setattr__(px, 'gender', gender_obj)
                    
                    if px.address_id:
                        from healthdatalayer.models.client.address import Address
                        address_obj = session.get(Address, px.address_id)
                        object.__setattr__(px, 'address', address_obj)
                    
                    if px.marriage_status_id:
                        from healthdatalayer.models.client.marriage_status import MarriageStatus
                        marriage_status_obj = session.get(MarriageStatus, px.marriage_status_id)
                        object.__setattr__(px, 'marriage_status', marriage_status_obj)
                    
                    if px.profession_id:
                        from healthdatalayer.models.client.profession import Profession
                        profession_obj = session.get(Profession, px.profession_id)
                        object.__setattr__(px, 'profession', profession_obj)
                    
                    if px.education_id:
                        from healthdatalayer.models.client.education import Education
                        education_obj = session.get(Education, px.education_id)
                        object.__setattr__(px, 'education', education_obj)
                    
                    if px.user_id:
                        from healthdatalayer.models.user.user import User
                        user_obj = session.get(User, px.user_id)
                        object.__setattr__(px, 'user', user_obj)
                        
                    if px.nationality_id:
                        from healthdatalayer.models.client.nationality import Nationality
                        user_obj = session.get(Nationality, px.nationality_id)
                        object.__setattr__(px, 'nationality', user_obj)
                    
                    from healthdatalayer.models.client.pathological_history import PathologicalHistory
                    statement = select(PathologicalHistory).where(PathologicalHistory.client_id == px.client_id)
                    pathological_his = session.exec(statement).all()
                    if pathological_his:
                        object.__setattr__(px, 'pathological_histories',pathological_his)
            
            
            return results
            
    def update_command(self, px: Px) -> Px:
        with get_session(self.tenant) as session:
            db_px = session.merge(px)
            session.commit()
            session.refresh(db_px)
            return db_px

    def delete_command(self, px_id: UUID, soft_delete: bool = True) -> bool:
        with get_session(self.tenant) as session:
            db_px = session.get(Px, px_id)
            if not db_px:
                return False
            
            if soft_delete:
                db_px.is_active = False
                session.add(db_px)
            else:
                session.delete(db_px)
            
            session.commit()
            return True
    
    def count_command(self, active_only: bool = True) -> int:
        with get_session(self.tenant) as session:
            statement = select(Px)
            if active_only:
                statement = statement.where(Px.is_active == True)
            results = session.exec(statement)
            return len(results.all())