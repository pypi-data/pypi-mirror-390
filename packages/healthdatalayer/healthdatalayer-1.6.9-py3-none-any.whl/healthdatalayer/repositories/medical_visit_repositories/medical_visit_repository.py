from typing import Optional, List
from datetime import datetime, date, time
from uuid import UUID
from sqlmodel import select, text
from sqlalchemy.orm import selectinload,joinedload
from healthdatalayer.models import MedicalVisit,MedicalDiagnosisVisit
from healthdatalayer.dtos import MedicalCertificateDTO,  DiagnosisDTO, MedicalDiagnosesDTO
from healthdatalayer.config.db import engines, get_session

class MedicalVisitRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")
    
    def create_command(self, medical_visit: MedicalVisit) -> MedicalVisit:
        with get_session(self.tenant) as session:
            session.add(medical_visit)
            session.commit()
            session.refresh(medical_visit)
            return medical_visit
    
    def get_by_id_command(self, medical_visit_id: UUID, load_relations: bool = False) -> Optional[MedicalVisit]:
        with get_session(self.tenant) as session:
            
            if load_relations:
                statement = select(MedicalVisit).where(MedicalVisit.medical_visit_id == medical_visit_id).options(
                    joinedload(MedicalVisit.client),
                    joinedload(MedicalVisit.collaborator),
                    joinedload(MedicalVisit.speciality),
                    selectinload(MedicalVisit.medical_diagnosis_visits).selectinload(MedicalDiagnosisVisit.medical_diagnosis),
                    selectinload(MedicalVisit.medical_recipe_visits),
                    selectinload(MedicalVisit.organ_system_reviews),
                    selectinload(MedicalVisit.physical_exams)
                )
                medical_visit = session.exec(statement).first()
               
                return medical_visit
            else:
                return session.get(MedicalVisit, medical_visit_id)
    
    def list_all_command(self, active_only: bool = True, load_relations: bool = False)->List[MedicalVisit]:
        with get_session(self.tenant) as session:
            statement = select(MedicalVisit)
            
            if load_relations:
                
                statement = select(MedicalVisit).options(
                    joinedload(MedicalVisit.client),
                    joinedload(MedicalVisit.collaborator),
                    joinedload(MedicalVisit.speciality),
                    selectinload(MedicalVisit.medical_diagnosis_visits),
                    selectinload(MedicalVisit.medical_recipe_visits),
                    selectinload(MedicalVisit.organ_system_reviews),
                    selectinload(MedicalVisit.physical_exams)
                )
                if active_only:
                    statement = statement.where(MedicalVisit.is_active == True)
                medical_visits = session.exec(statement).all()
              
                return medical_visits
            
            statement = select(MedicalVisit)
            return session.exec(statement).all()
    
    def get_by_client_id_command(self, client_id: UUID, active_only: bool = True, load_relations: bool = False) -> List[MedicalVisit]:
        with get_session(self.tenant) as session:
            statement = select(MedicalVisit).where(MedicalVisit.client_id == client_id)
            if active_only:
                statement = statement.where(MedicalVisit.is_active == True)
            if load_relations:
                statement = statement.options(
                    joinedload(MedicalVisit.client),
                    joinedload(MedicalVisit.collaborator),
                    joinedload(MedicalVisit.speciality),
                    selectinload(MedicalVisit.medical_diagnosis_visits).selectinload(MedicalDiagnosisVisit.medical_diagnosis),
                    selectinload(MedicalVisit.medical_recipe_visits),
                    selectinload(MedicalVisit.organ_system_reviews),
                    selectinload(MedicalVisit.physical_exams)
                )
            
            medical_visits = session.exec(statement).all()
            return medical_visits
        
    def get_by_collaborator_id_command(self, collaborator_id: UUID, active_only: bool = True, load_relations: bool = False) -> List[MedicalVisit]:
        with get_session(self.tenant) as session:
            statement = select(MedicalVisit).where(MedicalVisit.collaborator_id == collaborator_id)
            
            if active_only:
                statement = statement.where(MedicalVisit.is_active == True)
            if load_relations:
                statement = statement.options(
                    joinedload(MedicalVisit.client),
                    joinedload(MedicalVisit.collaborator),
                    joinedload(MedicalVisit.speciality),
                    selectinload(MedicalVisit.medical_diagnosis_visits).selectinload(MedicalDiagnosisVisit.medical_diagnosis),
                    selectinload(MedicalVisit.medical_recipe_visits),
                    selectinload(MedicalVisit.organ_system_reviews),
                    selectinload(MedicalVisit.physical_exams)
                )
            
            medical_visits = session.exec(statement).all()
            return medical_visits
        
    def get_by_next_followup_id_command(self, next_followup_id: UUID, active_only: bool = True, load_relations: bool = False) -> List[MedicalVisit]:
        with get_session(self.tenant) as session:
            statement = select(MedicalVisit).where(MedicalVisit.next_followup_visit_id == next_followup_id)
            
            if active_only:
                statement = statement.where(MedicalVisit.is_active == True)
            if load_relations:
                statement = statement.options(
                    joinedload(MedicalVisit.client),
                    joinedload(MedicalVisit.collaborator),
                    joinedload(MedicalVisit.speciality),
                    selectinload(MedicalVisit.medical_diagnosis_visits),
                    selectinload(MedicalVisit.medical_recipe_visits),
                    selectinload(MedicalVisit.organ_system_reviews),
                    selectinload(MedicalVisit.physical_exams)
                )
            
            medical_visits = session.exec(statement).all()
            return medical_visits

    def get_by_daterange_command(self, start_date: datetime, end_date: datetime, active_only: bool = True, load_relations: bool = False) -> List[MedicalVisit]:
        with get_session(self.tenant) as session:
            statement = select(MedicalVisit).where(
                    MedicalVisit.visit_date >= start_date
                )
            
            if end_date is not None:
                statement = statement.where(MedicalVisit.visit_date <= end_date)
            if active_only:
                statement = statement.where(MedicalVisit.is_active == True)
            if load_relations:
                statement = statement.options(
                    joinedload(MedicalVisit.client),
                    joinedload(MedicalVisit.collaborator),
                    joinedload(MedicalVisit.speciality),
                    selectinload(MedicalVisit.medical_diagnosis_visits).selectinload(MedicalDiagnosisVisit.medical_diagnosis),
                    selectinload(MedicalVisit.medical_recipe_visits),
                    selectinload(MedicalVisit.organ_system_reviews),
                    selectinload(MedicalVisit.physical_exams)
                )
            
            medical_visits = session.exec(statement).all()
            return medical_visits
        
    def get_by_targetdate_command(self, target_date: datetime, active_only: bool = True, load_relations: bool = False) -> List[MedicalVisit]:
        with get_session(self.tenant) as session:

            if isinstance(target_date, str):
                try:
                    target_date = datetime.strptime(target_date, "%Y-%m-%d")
                except ValueError:
                    raise ValueError("Invalid date format")

            elif isinstance(target_date, date) and not isinstance(target_date, datetime):
                target_date = datetime.combine(target_date, time.min)

            start_of_day = datetime.combine(target_date.date(), datetime.min.time())
            end_of_day = datetime.combine(target_date.date(), datetime.max.time())

            statement = select(MedicalVisit).where(
                    MedicalVisit.visit_date >= start_of_day,
                    MedicalVisit.visit_date <= end_of_day
                )

            if active_only:
                statement = statement.where(MedicalVisit.is_active == True)
            if load_relations:
                statement = statement.options(
                    joinedload(MedicalVisit.client),
                    joinedload(MedicalVisit.collaborator),
                    joinedload(MedicalVisit.speciality),
                    selectinload(MedicalVisit.medical_diagnosis_visits).selectinload(MedicalDiagnosisVisit.medical_diagnosis),
                    selectinload(MedicalVisit.medical_recipe_visits),
                    selectinload(MedicalVisit.organ_system_reviews),
                    selectinload(MedicalVisit.physical_exams)
                )
            
            medical_visits = session.exec(statement).all()
            return medical_visits

    def get_by_collaboratorid_and_daterange_command(self, collaborator_id: UUID, start_date: datetime, end_date: datetime, active_only: bool = True, load_relations: bool = False) -> List[MedicalVisit]:
        with get_session(self.tenant) as session:
            statement = select(MedicalVisit).where(
                    MedicalVisit.collaborator_id == collaborator_id,
                    MedicalVisit.visit_date >= start_date
                )
            
            if end_date is not None:
                statement = statement.where(MedicalVisit.visit_date <= end_date)
            if active_only:
                statement = statement.where(MedicalVisit.is_active == True)
            if load_relations:
                statement = statement.options(
                    joinedload(MedicalVisit.client),
                    joinedload(MedicalVisit.collaborator),
                    joinedload(MedicalVisit.speciality),
                    selectinload(MedicalVisit.medical_diagnosis_visits).selectinload(MedicalDiagnosisVisit.medical_diagnosis),
                    selectinload(MedicalVisit.medical_recipe_visits),
                    selectinload(MedicalVisit.organ_system_reviews),
                    selectinload(MedicalVisit.physical_exams)
                )
            
            medical_visits = session.exec(statement).all()
            return medical_visits
        
    def get_by_collaboratorid_and_targetdate_command(self, collaborator_id: UUID, target_date: datetime, active_only: bool = True, load_relations: bool = False) -> List[MedicalVisit]:
        with get_session(self.tenant) as session:

            if isinstance(target_date, str):
                try:
                    target_date = datetime.strptime(target_date, "%Y-%m-%d")
                except ValueError:
                    raise ValueError("Invalid date format")

            elif isinstance(target_date, date) and not isinstance(target_date, datetime):
                target_date = datetime.combine(target_date, time.min)

            start_of_day = datetime.combine(target_date.date(), datetime.min.time())
            end_of_day = datetime.combine(target_date.date(), datetime.max.time())

            statement = select(MedicalVisit).where(
                    MedicalVisit.collaborator_id == collaborator_id,
                    MedicalVisit.visit_date >= start_of_day,
                    MedicalVisit.visit_date <= end_of_day
                )

            if active_only:
                statement = statement.where(MedicalVisit.is_active == True)
            if load_relations:
                statement = statement.options(
                    joinedload(MedicalVisit.client),
                    joinedload(MedicalVisit.collaborator),
                    joinedload(MedicalVisit.speciality),
                    selectinload(MedicalVisit.medical_diagnosis_visits).selectinload(MedicalDiagnosisVisit.medical_diagnosis),
                    selectinload(MedicalVisit.medical_recipe_visits),
                    selectinload(MedicalVisit.organ_system_reviews),
                    selectinload(MedicalVisit.physical_exams)
                )
            
            medical_visits = session.exec(statement).all()
            return medical_visits
    
    def get_by_collaboratorid_and_specificdatetime_command(self, collaborator_id: UUID, specific_datetime: datetime, active_only: bool = True, load_relations: bool = False) -> Optional[MedicalVisit]:
        with get_session(self.tenant) as session:

            statement = select(MedicalVisit).where(
                    MedicalVisit.collaborator_id == collaborator_id,
                    MedicalVisit.visit_date == specific_datetime
                )

            if active_only:
                statement = statement.where(MedicalVisit.is_active == True)
            if load_relations:
                statement = statement.options(
                    joinedload(MedicalVisit.client),
                    joinedload(MedicalVisit.collaborator),
                    joinedload(MedicalVisit.speciality),
                    selectinload(MedicalVisit.medical_diagnosis_visits).selectinload(MedicalDiagnosisVisit.medical_diagnosis),
                    selectinload(MedicalVisit.medical_recipe_visits),
                    selectinload(MedicalVisit.organ_system_reviews),
                    selectinload(MedicalVisit.physical_exams)
                )
            
            medical_visit = session.exec(statement).first()
            return medical_visit
        
    def get_first_by_clientid_command(self, client_id: UUID, active_only: bool = True, load_relations: bool = False) -> Optional[MedicalVisit]:
        with get_session(self.tenant) as session:

            statement = select(MedicalVisit).where(MedicalVisit.client_id == client_id).order_by(MedicalVisit.visit_date.asc())

            if active_only:
                statement = statement.where(MedicalVisit.is_active == True)
            if load_relations:
                statement = statement.options(
                    joinedload(MedicalVisit.client),
                    joinedload(MedicalVisit.collaborator),
                    joinedload(MedicalVisit.speciality),
                    selectinload(MedicalVisit.medical_diagnosis_visits).selectinload(MedicalDiagnosisVisit.medical_diagnosis),
                    selectinload(MedicalVisit.medical_recipe_visits),
                    selectinload(MedicalVisit.organ_system_reviews),
                    selectinload(MedicalVisit.physical_exams)
                )
            
            medical_visit = session.exec(statement).first()
            return medical_visit
    
    def get_last_by_clientid_command(self, client_id: UUID, active_only: bool = True, load_relations: bool = False) -> Optional[MedicalVisit]:
        with get_session(self.tenant) as session:

            statement = select(MedicalVisit).where(MedicalVisit.client_id == client_id).order_by(MedicalVisit.visit_date.desc())

            if active_only:
                statement = statement.where(MedicalVisit.is_active == True)
            if load_relations:
                statement = statement.options(
                    joinedload(MedicalVisit.client),
                    joinedload(MedicalVisit.collaborator),
                    joinedload(MedicalVisit.speciality),
                    selectinload(MedicalVisit.medical_diagnosis_visits).selectinload(MedicalDiagnosisVisit.medical_diagnosis),
                    selectinload(MedicalVisit.medical_recipe_visits),
                    selectinload(MedicalVisit.organ_system_reviews),
                    selectinload(MedicalVisit.physical_exams)
                )
            
            medical_visit = session.exec(statement).first()
            return medical_visit
    
    def update_command(self, medical_visit: MedicalVisit) -> MedicalVisit:
        with get_session(self.tenant) as session:
            existing_medical_visit = session.get(MedicalVisit, medical_visit.medical_visit_id)
            if not existing_medical_visit:
                raise ValueError(f"medical_visit with id {medical_visit.medical_visit_id} does not exist")
            
            for key, value in medical_visit.dict(exclude_unset=True).items():
                setattr(existing_medical_visit, key, value)
            
            bd_medical_visit =  session.merge(existing_medical_visit)
            session.commit()
            session.refresh(bd_medical_visit)
            return bd_medical_visit
        
    def delete_command(self, medical_visit_id: UUID, soft_delete: bool = False)->None:
        with get_session(self.tenant) as session:
            existing_bridge = session.get(MedicalVisit, medical_visit_id)
            if not existing_bridge:
                raise ValueError(f"MedicalVisit with id {medical_visit_id} does not exist")

            if soft_delete:
                existing_bridge.is_active = False
                session.add(existing_bridge)
            else:
                session.delete(existing_bridge)

            session.commit()
    
    def exists_by_collaboratoid_and_targetdate_command(self, collaborator_id: UUID, target_date: datetime) -> bool:
        with get_session(self.tenant) as session:
            statement = select(MedicalVisit).where(MedicalVisit.collaborator_id == collaborator_id, MedicalVisit.visit_date == target_date)
            result = session.exec(statement).first()
            return result is not None
    
    
    def get_data_medical_certificate_command(self, medical_visit_id: str) -> MedicalCertificateDTO:
    
        with get_session(self.tenant) as session:
            
            query = text("""
                select 
                s."name"  as "sys",
                b2."name" as stablishment,
                px.medical_record_number,
                px.identification  as number_his,
                px.last_name ,
                px.first_name,
                case 
                    when g.name ='Male' then 'M'
                    else 'F'
                end as sex,
                EXTRACT(YEAR FROM AGE(px.birth_date)) AS age,
                sp.name as service,
                sp.subspeciality as speciality,
                EXTRACT(YEAR FROM mv.visit_date) AS year_visit,
                EXTRACT(MONTH FROM mv.visit_date) AS month_visit,
                EXTRACT(DAY FROM mv.visit_date) AS day_visit,
                mv.visit_date::time AS hour_start,
                (mv.visit_date + INTERVAL '30 minutes')::time AS hour_end,
                TO_CHAR(mv.visit_date, 'DD') || ' de ' ||
                CASE EXTRACT(MONTH FROM mv.visit_date)
                    WHEN 1 THEN 'enero'
                    WHEN 2 THEN 'febrero'
                    WHEN 3 THEN 'marzo'
                    WHEN 4 THEN 'abril'
                    WHEN 5 THEN 'mayo'
                    WHEN 6 THEN 'junio'
                    WHEN 7 THEN 'julio'
                    WHEN 8 THEN 'agosto'
                    WHEN 9 THEN 'septiembre'
                    WHEN 10 THEN 'octubre'
                    WHEN 11 THEN 'noviembre'
                    WHEN 12 THEN 'diciembre'
                END || ' del ' || EXTRACT(YEAR FROM mv.visit_date) AS visit_date_spanish,
                mv.rest,
                mv.rest_hours, 
                mv.rest_date_start , 
                EXTRACT(YEAR FROM mv.rest_date_start) AS year_rest_start,
                EXTRACT(MONTH FROM mv.rest_date_start) AS month_rest_start,
                EXTRACT(DAY FROM mv.rest_date_start) AS day_rest_start,
                TO_CHAR(mv.rest_date_start, 'DD') || ' de ' ||
                CASE EXTRACT(MONTH FROM mv.rest_date_start)
                    WHEN 1 THEN 'enero'
                    WHEN 2 THEN 'febrero'
                    WHEN 3 THEN 'marzo'
                    WHEN 4 THEN 'abril'
                    WHEN 5 THEN 'mayo'
                    WHEN 6 THEN 'junio'
                    WHEN 7 THEN 'julio'
                    WHEN 8 THEN 'agosto'
                    WHEN 9 THEN 'septiembre'
                    WHEN 10 THEN 'octubre'
                    WHEN 11 THEN 'noviembre'
                    WHEN 12 THEN 'diciembre'
                END || ' del ' || EXTRACT(YEAR FROM mv.rest_date_start) AS rest_date_start_spanish,
                mv.rest_date_end,
                EXTRACT(YEAR FROM mv.rest_date_end) AS year_rest_end,
                EXTRACT(MONTH FROM mv.rest_date_end) AS month_rest_end,
                EXTRACT(DAY FROM mv.rest_date_end) AS day_rest_end,
                TO_CHAR( mv.rest_date_end, 'DD') || ' de ' ||
                CASE EXTRACT(MONTH FROM  mv.rest_date_end)
                    WHEN 1 THEN 'enero'
                    WHEN 2 THEN 'febrero'
                    WHEN 3 THEN 'marzo'
                    WHEN 4 THEN 'abril'
                    WHEN 5 THEN 'mayo'
                    WHEN 6 THEN 'junio'
                    WHEN 7 THEN 'julio'
                    WHEN 8 THEN 'agosto'
                    WHEN 9 THEN 'septiembre'
                    WHEN 10 THEN 'octubre'
                    WHEN 11 THEN 'noviembre'
                    WHEN 12 THEN 'diciembre'
                END || ' del ' || EXTRACT(YEAR FROM  mv.rest_date_end) AS rest_date_end_spanish,
                c.name as doctor_name,
                c.ruc  as doctor_ruc
                from medical_visit mv
                left join px on px.client_id  = mv.client_id 
                left join gender g on g.gender_id  = px.gender_id 
                left join collaborator c on c.collaborator_id  = mv.collaborator_id 
                left join bridge_area_floor_branch b on b.bridge_area_floor_branch_id  = mv.bridge_area_floor_branch_id 
                left join branch b2 on b.branch_id  = b2.branch_id 
                left join "system" s on s.system_id  = b2.system_id 
                left join speciality sp on sp.speciality_id = mv.speciality_id
                where mv.medical_visit_id = :medical_visit_id
                and mv.status_visit != 'CANCELADO'
            """)
            
            result = session.exec(query, params={"medical_visit_id": medical_visit_id})
            
            row = result.fetchone()
        
            
            if not row:
                raise ValueError(f"No se encontró la visita médica con ID: {medical_visit_id}")
            
            
            return MedicalCertificateDTO(
                sys=row[0],
                stablishment=row[1],
                medical_record_number=row[2],
                number_his=row[3],
                last_name=row[4],
                first_name=row[5],
                sex=row[6],
                age=row[7],
                service=row[8],
                speciality=row[9],
                year_visit=row[10],
                month_visit=row[11],
                day_visit=row[12],
                hour_start=row[13],
                hour_end=row[14],
                visit_date_spanish=row[15],
                rest=row[16],
                rest_hours=row[17],
                rest_date_start=row[18],
                year_rest_start=row[19],
                month_rest_start=row[20],
                day_rest_start=row[21],
                rest_date_start_spanish=row[22],
                rest_date_end=row[23],
                year_rest_end=row[24],
                month_rest_end=row[25],
                day_rest_end=row[26],
                rest_date_end_spanish=row[27],
                doctor_name=row[28],
                doctor_ruc=row[29]
            )
    
    def get_medical_diagnoses_command(self, medical_visit_id: str) -> MedicalDiagnosesDTO:
    
        with get_session(self.tenant) as session:
            
            query = text("""
                select md."name" as name_diagnosis,
                md.cie_10_code 
                from medical_diagnosis md 
                join medical_diagnosis_visit mdv on mdv.medical_diagnosis_id  = md.medical_diagnosis_id 
                where md.is_active = true
                and mdv.is_active  = true
                and mdv.medical_visit_id  = :medical_visit_id
            """)
            
            result = session.exec(query, params={"medical_visit_id": medical_visit_id})
            rows = result.fetchall()
            
            # Convertir cada fila a DiagnosisDTO
            diagnoses_list = []
            for row in rows:
                diagnosis = DiagnosisDTO(
                    name_diagnosis=row[0],
                    cie_10_code=row[1]
                )
                diagnoses_list.append(diagnosis)
            
            return MedicalDiagnosesDTO(diagnoses=diagnoses_list)