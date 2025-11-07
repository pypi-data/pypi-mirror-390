from typing import Optional, List
from uuid import UUID
from sqlmodel import select

from healthdatalayer.models import MeasureLab
from healthdatalayer.config.db import engines, get_session

class MeasureLabRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")

    def create_command(self, measure_lab: MeasureLab) -> MeasureLab:
        with get_session(self.tenant) as session:
            session.add(measure_lab)
            session.commit()
            session.refresh(measure_lab)
            return measure_lab

    def get_by_id_command(self, measure_lab_id: UUID) -> Optional[MeasureLab]:
        with get_session(self.tenant) as session:
            return session.get(MeasureLab, measure_lab_id)

    def get_by_name_command(self, name: str) -> Optional[MeasureLab]:
        with get_session(self.tenant) as session:
            statement = select(MeasureLab).where(MeasureLab.name == name)
            return session.exec(statement).first()

    def search_by_name_command(self, name: str) -> List[MeasureLab]:
        with get_session(self.tenant) as session:
            statement = select(MeasureLab).where(MeasureLab.name.ilike(f"%{name}%"))
            results = session.exec(statement)
            return results.all()

    def list_all_command(self, active_only: bool = True) -> List[MeasureLab]:
        with get_session(self.tenant) as session:
            statement = select(MeasureLab)
            
            if active_only:
                statement = statement.where(MeasureLab.is_active == True)
            
            results = session.exec(statement)
            return results.all()

    def update_command(self, measure_lab: MeasureLab) -> MeasureLab:
        with get_session(self.tenant) as session:
            db_measure_lab = session.merge(measure_lab)
            session.commit()
            session.refresh(db_measure_lab)
            return db_measure_lab

    def delete_command(self, measure_lab_id: UUID, soft_delete: bool = True) -> bool:
        with get_session(self.tenant) as session:
            db_measure_lab = session.get(MeasureLab, measure_lab_id)
            if not db_measure_lab:
                return False
            
            if soft_delete:
                db_measure_lab.is_active = False
                session.add(db_measure_lab)
            else:
                session.delete(db_measure_lab)
            
            session.commit()
            return True

    def count_command(self, active_only: bool = True) -> int:
        with get_session(self.tenant) as session:
            statement = select(MeasureLab)
            if active_only:
                statement = statement.where(MeasureLab.is_active == True)
            results = session.exec(statement)
            return len(results.all())

    def exists_by_name_command(self, name: str) -> bool:
        with get_session(self.tenant) as session:
            statement = select(MeasureLab).where(MeasureLab.name == name)
            result = session.exec(statement).first()
            return result is not None