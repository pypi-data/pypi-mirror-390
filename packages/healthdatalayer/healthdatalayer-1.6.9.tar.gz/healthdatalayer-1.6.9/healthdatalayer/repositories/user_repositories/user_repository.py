from typing import Optional, List
from uuid import UUID
from sqlmodel import select
from sqlalchemy.orm import selectinload

from healthdatalayer.models import User
from healthdatalayer.models import Role
from healthdatalayer.models import Permission
from healthdatalayer.config.db import engines, get_session

class UserRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")

    def create_command(self, user: User) -> User:
        with get_session(self.tenant) as session:
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def get_by_id_command(self, user_id: UUID, load_relations: bool = False) -> Optional[User]:
        with get_session(self.tenant) as session:
            if load_relations:
                statement = select(User).where(User.user_id == user_id).options(
                    selectinload(User.roles),
                    selectinload(User.permissions)
                )
                return session.exec(statement).first()
            else:
                return session.get(User, user_id)

    def get_by_username_command(self, username: str, load_relations: bool = False) -> Optional[User]:
        with get_session(self.tenant) as session:
            statement = select(User).where(User.username == username)
            
            if load_relations:
                statement = statement.options(
                    selectinload(User.roles),
                    selectinload(User.permissions)
                )
            
            return session.exec(statement).first()

    def get_by_email_command(self, email: str, load_relations: bool = False) -> Optional[User]:
        with get_session(self.tenant) as session:
            statement = select(User).where(User.email == email)
            
            if load_relations:
                statement = statement.options(
                    selectinload(User.roles),
                    selectinload(User.permissions)
                )
            
            return session.exec(statement).first()

    def search_by_username_command(self, username: str, load_relations: bool = False) -> List[User]:
        with get_session(self.tenant) as session:
            statement = select(User).where(User.username.ilike(f"%{username}%"))
            
            if load_relations:
                statement = statement.options(
                    selectinload(User.roles),
                    selectinload(User.permissions)
                )
            
            results = session.exec(statement)
            return results.all()

    def list_all_command(self, active_only: bool = True, load_relations: bool = False) -> List[User]:
        with get_session(self.tenant) as session:
            statement = select(User)
            
            if active_only:
                statement = statement.where(User.is_active == True)
            
            if load_relations:
                statement = statement.options(
                    selectinload(User.roles),
                    selectinload(User.permissions)
                )
            
            results = session.exec(statement)
            return results.all()

    def update_command(self, user: User) -> User:
        with get_session(self.tenant) as session:
            db_user = session.merge(user)
            session.commit()
            session.refresh(db_user)
            return db_user

    def delete_command(self, user_id: UUID, soft_delete: bool = True) -> bool:
        with get_session(self.tenant) as session:
            db_user = session.get(User, user_id)
            if not db_user:
                return False
            
            if soft_delete:
                db_user.is_active = False
                session.add(db_user)
            else:
                session.delete(db_user)
            
            session.commit()
            return True

    def count_command(self, active_only: bool = True) -> int:
        with get_session(self.tenant) as session:
            statement = select(User)
            if active_only:
                statement = statement.where(User.is_active == True)
            results = session.exec(statement)
            return len(results.all())

    def exists_by_username_command(self, username: str) -> bool:
        with get_session(self.tenant) as session:
            statement = select(User).where(User.username == username)
            result = session.exec(statement).first()
            return result is not None

    def exists_by_email_command(self, email: str) -> bool:
        with get_session(self.tenant) as session:
            statement = select(User).where(User.email == email)
            result = session.exec(statement).first()
            return result is not None

    def change_password_command(self, user_id: UUID, new_password: str) -> Optional[User]:
        with get_session(self.tenant) as session:
            user = session.get(User, user_id)
            if not user:
                return None
            user.password = new_password
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        
    # ROLES COMANDS

    def get_user_roles_command(self, user_id: UUID) -> List[Role]:
        with get_session(self.tenant) as session:
            statement = select(User).options(selectinload(User.roles)).where(User.user_id == user_id)
            user = session.exec(statement).first()
            if not user:
                return []
            return user.roles
    
    def has_role_command(self, user_id: UUID, role_name: str) -> bool:
        with get_session(self.tenant) as session:
            statement = select(User).options(selectinload(User.roles)).where(User.user_id == user_id)
            user = session.exec(statement).first()
            if not user:
                return False
            return any(role.name == role_name for role in user.roles)
    
    def assign_role_command(self, user_id: UUID, role_id: UUID) -> Optional[User]:
        with get_session(self.tenant) as session:
            user_statement = select(User).options(selectinload(User.roles)).where(User.user_id == user_id)
            user = session.exec(user_statement).first()
            if not user:
                return None
            
            role = session.get(Role, role_id)
            if not role:
                return None
            
            if role not in user.roles:
                user.roles.append(role)
                session.add(user)
                session.commit()
                session.refresh(user)
            
            return user

    def remove_role_command(self, user_id: UUID, role_id: UUID) -> Optional[User]:
        with get_session(self.tenant) as session:
            user_statement = select(User).options(selectinload(User.roles)).where(User.user_id == user_id)
            user = session.exec(user_statement).first()
            if not user:
                return None
            
            role = session.get(Role, role_id)
            if not role:
                return None
            
            if role in user.roles:
                user.roles.remove(role)
                session.add(user)
                session.commit()
                session.refresh(user)
            
            return user
        
    # PERMISSIONS COMANDS

    def get_user_permissions_command(self, user_id: UUID) -> List[Permission]:
        with get_session(self.tenant) as session:
            statement = select(User).options(selectinload(User.permissions)).where(User.user_id == user_id)
            user = session.exec(statement).first()
            if not user:
                return []
            return user.permissions

    def has_permission_command(self, user_id: UUID, permission_name: str) -> bool:
        with get_session(self.tenant) as session:
            statement = select(User).options(selectinload(User.permissions)).where(User.user_id == user_id)
            user = session.exec(statement).first()
            if not user:
                return False
            return any(perm.name == permission_name for perm in user.permissions)

    def assign_permission_command(self, user_id: UUID, permission_id: UUID) -> Optional[User]:
        with get_session(self.tenant) as session:
            user_statement = select(User).options(selectinload(User.permissions)).where(User.user_id == user_id)
            user = session.exec(user_statement).first()
            if not user:
                return None
            
            permission = session.get(Permission, permission_id)
            if not permission:
                return None
            
            if permission not in user.permissions:
                user.permissions.append(permission)
                session.add(user)
                session.commit()
                session.refresh(user)
            
            return user

    def remove_permission_command(self, user_id: UUID, permission_id: UUID) -> Optional[User]:
        with get_session(self.tenant) as session:
            user_statement = select(User).options(selectinload(User.permissions)).where(User.user_id == user_id)
            user = session.exec(user_statement).first()
            if not user:
                return None
            
            permission = session.get(Permission, permission_id)
            if not permission:
                return None
            
            if permission in user.permissions:
                user.permissions.remove(permission)
                session.add(user)
                session.commit()
                session.refresh(user)
            
            return user