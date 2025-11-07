from typing import Optional, List
from uuid import UUID
from sqlmodel import select
from sqlalchemy.orm import selectinload

from healthdatalayer.models import Role
from healthdatalayer.models import Permission
from healthdatalayer.models import User
from healthdatalayer.config.db import engines, get_session

class RoleRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")

    def create_command(self, role: Role) -> Role:
        with get_session(self.tenant) as session:
            session.add(role)
            session.commit()
            session.refresh(role)
            return role

    def get_by_id_command(self, role_id: UUID, load_relations: bool = False) -> Optional[Role]:
        with get_session(self.tenant) as session:
            if load_relations:
                statement = select(Role).where(Role.role_id == role_id).options(
                    selectinload(Role.permissions),
                    selectinload(Role.users)
                )
                return session.exec(statement).first()
            else:
                return session.get(Role, role_id)

    def get_by_name_command(self, name: str, load_relations: bool = False) -> Optional[Role]:
        with get_session(self.tenant) as session:
            statement = select(Role).where(Role.name == name)
            
            if load_relations:
                statement = statement.options(
                    selectinload(Role.permissions),
                    selectinload(Role.users)
                )
            
            return session.exec(statement).first()

    def search_by_name_command(self, name: str, load_relations: bool = False) -> List[Role]:
        with get_session(self.tenant) as session:
            statement = select(Role).where(Role.name.ilike(f"%{name}%"))
            
            if load_relations:
                statement = statement.options(
                    selectinload(Role.permissions),
                    selectinload(Role.users)
                )
            
            results = session.exec(statement)
            return results.all()

    def list_all_command(self, active_only: bool = True, load_relations: bool = False) -> List[Role]:
        with get_session(self.tenant) as session:
            statement = select(Role)
            
            if active_only:
                statement = statement.where(Role.is_active == True)
            
            if load_relations:
                statement = statement.options(
                    selectinload(Role.permissions),
                    selectinload(Role.users)
                )
            
            results = session.exec(statement)
            return results.all()

    def update_command(self, role: Role) -> Role:
        with get_session(self.tenant) as session:
            db_role = session.merge(role)
            session.commit()
            session.refresh(db_role)
            return db_role

    def delete_command(self, role_id: UUID, soft_delete: bool = True) -> bool:
        with get_session(self.tenant) as session:
            db_role = session.get(Role, role_id)
            if not db_role:
                return False
            
            if soft_delete:
                db_role.is_active = False
                session.add(db_role)
            else:
                session.delete(db_role)
            
            session.commit()
            return True

    def count_command(self, active_only: bool = True) -> int:
        with get_session(self.tenant) as session:
            statement = select(Role)
            if active_only:
                statement = statement.where(Role.is_active == True)
            results = session.exec(statement)
            return len(results.all())

    def exists_by_name_command(self, name: str) -> bool:
        with get_session(self.tenant) as session:
            statement = select(Role).where(Role.name == name)
            result = session.exec(statement).first()
            return result is not None
        
    # RELATIONS COMMANDS

    def get_role_permissions_command(self, role_id: UUID) -> List[Permission]:
        with get_session(self.tenant) as session:
            statement = select(Role).options(selectinload(Role.permissions)).where(Role.role_id == role_id)
            role = session.exec(statement).first()
            if not role:
                return []
            return role.permissions

    def get_role_users_command(self, role_id: UUID) -> List[User]:
        with get_session(self.tenant) as session:
            statement = select(Role).options(selectinload(Role.users)).where(Role.role_id == role_id)
            role = session.exec(statement).first()
            if not role:
                return []
            return role.users

    def assign_permission_command(self, role_id: UUID, permission_id: UUID) -> Optional[Role]:
        with get_session(self.tenant) as session:
            role_statement = select(Role).options(selectinload(Role.permissions)).where(Role.role_id == role_id)
            role = session.exec(role_statement).first()
            if not role:
                return None
            
            permission = session.get(Permission, permission_id)
            if not permission:
                return None
            
            if permission not in role.permissions:
                role.permissions.append(permission)
                session.add(role)
                session.commit()
                session.refresh(role)
            
            return role

    def remove_permission_command(self, role_id: UUID, permission_id: UUID) -> Optional[Role]:
        with get_session(self.tenant) as session:
            role_statement = select(Role).options(selectinload(Role.permissions)).where(Role.role_id == role_id)
            role = session.exec(role_statement).first()
            if not role:
                return None
            
            permission = session.get(Permission, permission_id)
            if not permission:
                return None
            
            if permission in role.permissions:
                role.permissions.remove(permission)
                session.add(role)
                session.commit()
                session.refresh(role)
            
            return role

    def has_permission_command(self, role_id: UUID, permission_name: str) -> bool:
        with get_session(self.tenant) as session:
            statement = select(Role).options(selectinload(Role.permissions)).where(Role.role_id == role_id)
            role = session.exec(statement).first()
            if not role:
                return False
            return any(perm.name == permission_name for perm in role.permissions)