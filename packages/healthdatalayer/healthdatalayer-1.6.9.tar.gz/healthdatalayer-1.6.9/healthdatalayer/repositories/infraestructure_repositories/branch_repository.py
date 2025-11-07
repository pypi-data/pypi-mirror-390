from typing import Optional, List
from uuid import UUID
from sqlmodel import select

from healthdatalayer.models import Branch
from healthdatalayer.config.db import engines, get_session

class BranchRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")
    
    def create_command(self, branch: Branch) -> Branch:
        with get_session(self.tenant) as session:
            session.add(branch)
            session.commit()
            session.refresh(branch)
            return branch
    
    def get_by_id_command(self, branch_id: UUID) -> Optional[Branch]:
        with get_session(self.tenant) as session:
            return session.get(Branch, branch_id)
    
    def get_by_name_command(self, name: str) -> Optional[Branch]:
        with get_session(self.tenant) as session:
            statement = select(Branch).where(Branch.name == name)
            result = session.exec(statement).first()
            return result
    
    def list_all_command(self, active_only: bool = True) -> List[Branch]:
        with get_session(self.tenant) as session:
            statement = select(Branch)
            
            if active_only:
                statement = statement.where(Branch.is_active == True)
            
            results = session.exec(statement)
            return results.all()
    
    def update_command(self, branch_id: UUID, **kwargs) -> Optional[Branch]:
        with get_session(self.tenant) as session:
            db_branch = session.get(Branch, branch_id)
            if not db_branch:
                return None
            
            for key, value in kwargs.items():
                if hasattr(db_branch, key):
                    setattr(db_branch, key, value)
            
            session.add(db_branch)
            session.commit()
            session.refresh(db_branch)
            return db_branch
    
    def delete_command(self, branch_id: UUID, soft_delete: bool = True) -> bool:
        with get_session(self.tenant) as session:
            db_branch = session.get(Branch, branch_id)
            if not db_branch:
                return False
            
            if soft_delete:
                db_branch.is_active = False
                session.add(db_branch)
            else:
                session.delete(db_branch)
            
            session.commit()
            return True