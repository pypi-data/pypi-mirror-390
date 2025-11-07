from typing import Optional, List
from uuid import UUID
from sqlmodel import select
from sqlalchemy.orm import selectinload

from healthdatalayer.models import Permission
from healthdatalayer.models import Role
from healthdatalayer.models import User
from healthdatalayer.config.db import engines, get_session

class PermissionRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")

    def create_command(self, permission: Permission) -> Permission:
        with get_session(self.tenant) as session:
            session.add(permission)
            session.commit()
            session.refresh(permission)
            return permission

    def get_by_id_command(self, permission_id: UUID, load_relations: bool = False) -> Optional[Permission]:
        with get_session(self.tenant) as session:
            if load_relations:
                statement = select(Permission).where(Permission.permission_id == permission_id).options(
                    selectinload(Permission.roles),
                    selectinload(Permission.users)
                )
                return session.exec(statement).first()
            else:
                return session.get(Permission, permission_id)

    def get_by_name_command(self, name: str, load_relations: bool = False) -> Optional[Permission]:
        with get_session(self.tenant) as session:
            statement = select(Permission).where(Permission.name == name)
            
            if load_relations:
                statement = statement.options(
                    selectinload(Permission.roles),
                    selectinload(Permission.users)
                )
            
            return session.exec(statement).first()

    def search_by_name_command(self, name: str, load_relations: bool = False) -> List[Permission]:
        with get_session(self.tenant) as session:
            statement = select(Permission).where(Permission.name.ilike(f"%{name}%"))
            
            if load_relations:
                statement = statement.options(
                    selectinload(Permission.roles),
                    selectinload(Permission.users)
                )
            
            results = session.exec(statement)
            return results.all()

    def list_all_command(self, active_only: bool = True, load_relations: bool = False) -> List[Permission]:
        with get_session(self.tenant) as session:
            statement = select(Permission)
            
            if active_only:
                statement = statement.where(Permission.is_active == True)
            
            if load_relations:
                statement = statement.options(
                    selectinload(Permission.roles),
                    selectinload(Permission.users)
                )
            
            results = session.exec(statement)
            return results.all()

    def update_command(self, permission: Permission) -> Permission:
        with get_session(self.tenant) as session:
            db_permission = session.merge(permission)
            session.commit()
            session.refresh(db_permission)
            return db_permission

    def delete_command(self, permission_id: UUID, soft_delete: bool = True) -> bool:
        with get_session(self.tenant) as session:
            db_permission = session.get(Permission, permission_id)
            if not db_permission:
                return False
            
            if soft_delete:
                db_permission.is_active = False
                session.add(db_permission)
            else:
                session.delete(db_permission)
            
            session.commit()
            return True

    def count_command(self, active_only: bool = True) -> int:
        with get_session(self.tenant) as session:
            statement = select(Permission)
            if active_only:
                statement = statement.where(Permission.is_active == True)
            results = session.exec(statement)
            return len(results.all())

    def exists_by_name_command(self, name: str) -> bool:
        with get_session(self.tenant) as session:
            statement = select(Permission).where(Permission.name == name)
            result = session.exec(statement).first()
            return result is not None
        
    # ROLE COMMANDS    

    def get_permission_roles_command(self, permission_id: UUID) -> List[Role]:
        with get_session(self.tenant) as session:
            statement = select(Permission).options(selectinload(Permission.roles)).where(
                Permission.permission_id == permission_id
            )
            permission = session.exec(statement).first()
            if not permission:
                return []
            return permission.roles
    
    def assign_to_role_command(self, permission_id: UUID, role_id: UUID) -> Optional[Permission]:
        with get_session(self.tenant) as session:
            permission_statement = select(Permission).options(selectinload(Permission.roles)).where(
                Permission.permission_id == permission_id
            )
            permission = session.exec(permission_statement).first()
            if not permission:
                return None
            
            role = session.get(Role, role_id)
            if not role:
                return None
            
            if role not in permission.roles:
                permission.roles.append(role)
                session.add(permission)
                session.commit()
                session.refresh(permission)
            
            return permission

    def remove_from_role_command(self, permission_id: UUID, role_id: UUID) -> Optional[Permission]:
        with get_session(self.tenant) as session:
            permission_statement = select(Permission).options(selectinload(Permission.roles)).where(
                Permission.permission_id == permission_id
            )
            permission = session.exec(permission_statement).first()
            if not permission:
                return None
            
            role = session.get(Role, role_id)
            if not role:
                return None
            
            if role in permission.roles:
                permission.roles.remove(role)
                session.add(permission)
                session.commit()
                session.refresh(permission)
            
            return permission
    
    def is_assigned_to_role_command(self, permission_id: UUID, role_id: UUID) -> bool:
        with get_session(self.tenant) as session:
            statement = select(Permission).options(selectinload(Permission.roles)).where(
                Permission.permission_id == permission_id
            )
            permission = session.exec(statement).first()
            if not permission:
                return False
            return any(role.role_id == role_id for role in permission.roles)
    
    # USER COMMANDS    

    def get_permission_users_command(self, permission_id: UUID) -> List[User]:
        with get_session(self.tenant) as session:
            statement = select(Permission).options(selectinload(Permission.users)).where(
                Permission.permission_id == permission_id
            )
            permission = session.exec(statement).first()
            if not permission:
                return []
            return permission.users

    def assign_to_user_command(self, permission_id: UUID, user_id: UUID) -> Optional[Permission]:
        with get_session(self.tenant) as session:
            permission_statement = select(Permission).options(selectinload(Permission.users)).where(
                Permission.permission_id == permission_id
            )
            permission = session.exec(permission_statement).first()
            if not permission:
                return None
            
            user = session.get(User, user_id)
            if not user:
                return None
            
            if user not in permission.users:
                permission.users.append(user)
                session.add(permission)
                session.commit()
                session.refresh(permission)
            
            return permission

    def remove_from_user_command(self, permission_id: UUID, user_id: UUID) -> Optional[Permission]:
        with get_session(self.tenant) as session:
            permission_statement = select(Permission).options(selectinload(Permission.users)).where(
                Permission.permission_id == permission_id
            )
            permission = session.exec(permission_statement).first()
            if not permission:
                return None
            
            user = session.get(User, user_id)
            if not user:
                return None
            
            if user in permission.users:
                permission.users.remove(user)
                session.add(permission)
                session.commit()
                session.refresh(permission)
            
            return permission

    def is_assigned_to_user_command(self, permission_id: UUID, user_id: UUID) -> bool:
        with get_session(self.tenant) as session:
            statement = select(Permission).options(selectinload(Permission.users)).where(
                Permission.permission_id == permission_id
            )
            permission = session.exec(statement).first()
            if not permission:
                return False
            return any(user.user_id == user_id for user in permission.users)