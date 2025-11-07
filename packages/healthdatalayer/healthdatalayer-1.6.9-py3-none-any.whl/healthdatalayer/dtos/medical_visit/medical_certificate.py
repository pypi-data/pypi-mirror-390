from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime, time

class MedicalCertificateDTO(BaseModel):
    sys: Optional[str] = None
    stablishment: Optional[str] = None
    
    
    medical_record_number: Optional[str] = None
    number_his: Optional[str] = None
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    sex: Optional[str] = None
    age: Optional[int] = None
    
    
    service: Optional[str] = None
    speciality: Optional[str] = None
    
    
    year_visit: Optional[int] = None
    month_visit: Optional[int] = None
    day_visit: Optional[int] = None
    hour_start: Optional[time] = None
    hour_end: Optional[time] = None
    visit_date_spanish: Optional[str] = None
    
    
    rest: Optional[bool] = None
    rest_hours: Optional[float] = None
    rest_date_start: Optional[datetime] = None
    
    
    year_rest_start: Optional[int] = None
    month_rest_start: Optional[int] = None
    day_rest_start: Optional[int] = None
    rest_date_start_spanish: Optional[str] = None
    
    
    rest_date_end: Optional[datetime] = None
    
    
    year_rest_end: Optional[int] = None
    month_rest_end: Optional[int] = None
    day_rest_end: Optional[int] = None
    rest_date_end_spanish: Optional[str] = None
    
    
    doctor_name: Optional[str] = None
    doctor_ruc: Optional[str] = None


class DiagnosisDTO(BaseModel):
    name_diagnosis: str
    cie_10_code: Optional[str] = None

class MedicalDiagnosesDTO(BaseModel):
    diagnoses: List[DiagnosisDTO]

    class Config:
        from_attributes = True