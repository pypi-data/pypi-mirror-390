from typing import Optional, List
from uuid import UUID
from sqlmodel import select

from healthdatalayer.models import MedicalLab
from healthdatalayer.models import Px
from healthdatalayer.config.db import engines, get_session

class MedicalLabRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")

    def create_command(self, medical_lab: MedicalLab) -> MedicalLab:
        with get_session(self.tenant) as session:
            session.add(medical_lab)
            session.commit()
            session.refresh(medical_lab)
            return medical_lab

    def get_by_id_command(self, medical_lab_id: UUID, load_relations: bool = False) -> Optional[MedicalLab]:
        with get_session(self.tenant) as session:
            medical_lab = session.get(MedicalLab, medical_lab_id)
            
            if medical_lab and load_relations:
                if medical_lab.measure_lab_id:
                    from healthdatalayer.models import MeasureLab
                    measure_lab_obj = session.get(MeasureLab, medical_lab.measure_lab_id)
                    object.__setattr__(medical_lab, 'measure_lab', measure_lab_obj)
                
                from healthdatalayer.models.lab.client_lab import ClientLab
                statement = select(ClientLab).where(ClientLab.medical_lab_id == medical_lab_id)
                client_labs = session.exec(statement).all()
                
                pxs_list = []
                for cl in client_labs:
                    px = session.get(Px, cl.client_id)
                    if px:
                        pxs_list.append(px)
                
                object.__setattr__(medical_lab, 'pxs', pxs_list)
            
            return medical_lab

    def get_by_parameter_command(self, parameter: str, load_relations: bool = False) -> Optional[MedicalLab]:
        with get_session(self.tenant) as session:
            statement = select(MedicalLab).where(MedicalLab.parameter == parameter)
            medical_lab = session.exec(statement).first()
            
            if medical_lab and load_relations:
                if medical_lab.measure_lab_id:
                    from healthdatalayer.models import MeasureLab
                    measure_lab_obj = session.get(MeasureLab, medical_lab.measure_lab_id)
                    object.__setattr__(medical_lab, 'measure_lab', measure_lab_obj)
                
                from healthdatalayer.models.lab.client_lab import ClientLab
                statement_cl = select(ClientLab).where(ClientLab.medical_lab_id == medical_lab.medical_lab_id)
                client_labs = session.exec(statement_cl).all()
                
                pxs_list = []
                for cl in client_labs:
                    px = session.get(Px, cl.client_id)
                    if px:
                        pxs_list.append(px)
                
                object.__setattr__(medical_lab, 'pxs', pxs_list)
            
            return medical_lab

    def search_by_parameter_command(self, parameter: str, load_relations: bool = False) -> List[MedicalLab]:
        with get_session(self.tenant) as session:
            statement = select(MedicalLab).where(MedicalLab.parameter.ilike(f"%{parameter}%"))
            results = session.exec(statement).all()
            
            if load_relations:
                from healthdatalayer.models import MeasureLab
                from healthdatalayer.models.lab.client_lab import ClientLab
                
                for medical_lab in results:
                    if medical_lab.measure_lab_id:
                        measure_lab_obj = session.get(MeasureLab, medical_lab.measure_lab_id)
                        object.__setattr__(medical_lab, 'measure_lab', measure_lab_obj)
                    
                    statement_cl = select(ClientLab).where(ClientLab.medical_lab_id == medical_lab.medical_lab_id)
                    client_labs = session.exec(statement_cl).all()
                    
                    pxs_list = []
                    for cl in client_labs:
                        px = session.get(Px, cl.client_id)
                        if px:
                            pxs_list.append(px)
                    
                    object.__setattr__(medical_lab, 'pxs', pxs_list)
            
            return results

    def list_all_command(self, active_only: bool = True, load_relations: bool = False) -> List[MedicalLab]:
        with get_session(self.tenant) as session:
            statement = select(MedicalLab)
            
            if active_only:
                statement = statement.where(MedicalLab.is_active == True)
            
            results = session.exec(statement).all()
            
            if load_relations:
                from healthdatalayer.models import MeasureLab
                from healthdatalayer.models.lab.client_lab import ClientLab
                
                for medical_lab in results:
                    if medical_lab.measure_lab_id:
                        measure_lab_obj = session.get(MeasureLab, medical_lab.measure_lab_id)
                        object.__setattr__(medical_lab, 'measure_lab', measure_lab_obj)
                    
                    statement_cl = select(ClientLab).where(ClientLab.medical_lab_id == medical_lab.medical_lab_id)
                    client_labs = session.exec(statement_cl).all()
                    
                    pxs_list = []
                    for cl in client_labs:
                        px = session.get(Px, cl.client_id)
                        if px:
                            pxs_list.append(px)
                    
                    object.__setattr__(medical_lab, 'pxs', pxs_list)
            
            return results

    def list_by_measure_lab_command(self, measure_lab_id: UUID, active_only: bool = True) -> List[MedicalLab]:
        with get_session(self.tenant) as session:
            statement = select(MedicalLab).where(MedicalLab.measure_lab_id == measure_lab_id)
            
            if active_only:
                statement = statement.where(MedicalLab.is_active == True)
            
            results = session.exec(statement)
            return results.all()

    def update_command(self, medical_lab: MedicalLab) -> MedicalLab:
        with get_session(self.tenant) as session:
            db_medical_lab = session.merge(medical_lab)
            session.commit()
            session.refresh(db_medical_lab)
            return db_medical_lab

    def delete_command(self, medical_lab_id: UUID, soft_delete: bool = True) -> bool:
        with get_session(self.tenant) as session:
            db_medical_lab = session.get(MedicalLab, medical_lab_id)
            if not db_medical_lab:
                return False
            
            if soft_delete:
                db_medical_lab.is_active = False
                session.add(db_medical_lab)
            else:
                session.delete(db_medical_lab)
            
            session.commit()
            return True

    def count_command(self, active_only: bool = True) -> int:
        with get_session(self.tenant) as session:
            statement = select(MedicalLab)
            if active_only:
                statement = statement.where(MedicalLab.is_active == True)
            results = session.exec(statement)
            return len(results.all())

    def exists_by_parameter_command(self, parameter: str) -> bool:
        with get_session(self.tenant) as session:
            statement = select(MedicalLab).where(MedicalLab.parameter == parameter)
            result = session.exec(statement).first()
            return result is not None

    def get_medical_lab_patients_command(self, medical_lab_id: UUID) -> List[Px]:
        """Get all patients associated with a medical lab"""
        with get_session(self.tenant) as session:
            from healthdatalayer.models.lab.client_lab import ClientLab
            
            statement = select(ClientLab).where(ClientLab.medical_lab_id == medical_lab_id)
            client_labs = session.exec(statement).all()
            
            pxs_list = []
            for cl in client_labs:
                px = session.get(Px, cl.client_id)
                if px:
                    pxs_list.append(px)
            
            return pxs_list

    def assign_patient_command(self, medical_lab_id: UUID, px_id: UUID) -> Optional[MedicalLab]:
        """Assign a patient to a medical lab"""
        with get_session(self.tenant) as session:
            from healthdatalayer.models.lab.client_lab import ClientLab
            
            medical_lab = session.get(MedicalLab, medical_lab_id)
            if not medical_lab:
                return None
            
            px = session.get(Px, px_id)
            if not px:
                return None
            
            existing = session.exec(
                select(ClientLab).where(
                    ClientLab.medical_lab_id == medical_lab_id,
                    ClientLab.client_id == px_id
                )
            ).first()
            
            if not existing:
                client_lab = ClientLab(medical_lab_id=medical_lab_id, client_id=px_id)
                session.add(client_lab)
                session.commit()
            
            session.refresh(medical_lab)
            return medical_lab

    def remove_patient_command(self, medical_lab_id: UUID, px_id: UUID) -> Optional[MedicalLab]:
        """Remove a patient from a medical lab"""
        with get_session(self.tenant) as session:
            from healthdatalayer.models.lab.client_lab import ClientLab
            
            medical_lab = session.get(MedicalLab, medical_lab_id)
            if not medical_lab:
                return None
            
            client_lab = session.exec(
                select(ClientLab).where(
                    ClientLab.medical_lab_id == medical_lab_id,
                    ClientLab.client_id == px_id
                )
            ).first()
            
            if client_lab:
                session.delete(client_lab)
                session.commit()
            
            session.refresh(medical_lab)
            return medical_lab

    def is_patient_assigned_command(self, medical_lab_id: UUID, px_id: UUID) -> bool:
        """Check if a patient is assigned to a medical lab"""
        with get_session(self.tenant) as session:
            from healthdatalayer.models.lab.client_lab import ClientLab
            
            result = session.exec(
                select(ClientLab).where(
                    ClientLab.medical_lab_id == medical_lab_id,
                    ClientLab.client_id == px_id
                )
            ).first()
            
            return result is not None