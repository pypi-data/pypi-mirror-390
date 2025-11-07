from typing import Optional, List
from uuid import UUID
from sqlmodel import select, or_
from sqlalchemy.orm import selectinload,joinedload
from healthdatalayer.models import MedicalRecipeVisit, MedicalDrugRecipe, MedicalDrug
from healthdatalayer.config.db import engines, get_session

class MedicalRecipeVisitRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")
        
    def create_command(self, medical_recipe_visit: MedicalRecipeVisit) -> MedicalRecipeVisit:
        with get_session(self.tenant) as session:
            session.add(medical_recipe_visit)
            session.commit()
            session.refresh(medical_recipe_visit)
            return medical_recipe_visit
    
    def get_by_id_command(self, medical_recipe_visit_id: UUID, load_relations: bool = False) -> Optional[MedicalRecipeVisit]:
        with get_session(self.tenant) as session:
            
            if load_relations:
                statement = select(MedicalRecipeVisit).where(MedicalRecipeVisit.medical_recipe_visit_id == medical_recipe_visit_id).options(
                    joinedload(MedicalRecipeVisit.medical_visit),
                    selectinload(MedicalRecipeVisit.medical_drug_recipes).selectinload(MedicalDrugRecipe.medical_drug)
                )
                medical_recipe_visit = session.exec(statement).first()
               
                return medical_recipe_visit
            else:
                return session.get(MedicalRecipeVisit, medical_recipe_visit_id)
    
    def get_by_medical_visit_id_command(self, medical_visit_id: UUID, load_relations: bool = False) -> Optional[MedicalRecipeVisit]:
        with get_session(self.tenant) as session:
            statement = select(MedicalRecipeVisit).where(MedicalRecipeVisit.medical_visit_id == medical_visit_id)
            if load_relations:
                statement = statement.options(
                    selectinload(MedicalRecipeVisit.medical_visit),
                    selectinload(MedicalRecipeVisit.medical_drug_recipes).selectinload(MedicalDrugRecipe.medical_drug)
                )
            medical_recipe_visit = session.exec(statement).first()
               
            return medical_recipe_visit
            
    def list_all_command(self, active_only: bool = True, load_relations: bool = False)->List[MedicalRecipeVisit]:
        with get_session(self.tenant) as session:
            statement = select(MedicalRecipeVisit)
            
            if load_relations:
                
                statement = select(MedicalRecipeVisit).options(
                    selectinload(MedicalRecipeVisit.medical_visit),
                    selectinload(MedicalRecipeVisit.medical_drug_recipes).selectinload(MedicalDrugRecipe.medical_drug)
                )
                if active_only:
                    statement = statement.where(MedicalRecipeVisit.is_active == True)
                medical_recipe_visit = session.exec(statement).all()
              
                return medical_recipe_visit
            
            statement = select(MedicalRecipeVisit)
            return session.exec(statement).all()
    
    def update_command(self, medical_recipe_visit: MedicalRecipeVisit) -> MedicalRecipeVisit:
        with get_session(self.tenant) as session:
            existing_medical_recipe_visit = session.get(MedicalRecipeVisit, medical_recipe_visit.medical_recipe_visit_id)
            if not existing_medical_recipe_visit:
                raise ValueError(f"medical_recipe_visit with id {medical_recipe_visit.medical_recipe_visit_id} does not exist")
            
            for key, value in medical_recipe_visit.dict(exclude_unset=True).items():
                setattr(existing_medical_recipe_visit, key, value)
            
            bd_medical_recipe_visit =  session.merge(existing_medical_recipe_visit)
            session.commit()
            session.refresh(bd_medical_recipe_visit)
            return bd_medical_recipe_visit
        
    def delete_command(self, medical_recipe_visit_id: UUID, soft_delete: bool = False)->None:
        with get_session(self.tenant) as session:
            existing_medical_recipe_visit = session.get(MedicalRecipeVisit, medical_recipe_visit_id)
            if not existing_medical_recipe_visit:
                raise ValueError(f"MedicalRecipeVisit with id {medical_recipe_visit_id} does not exist")

            if soft_delete:
                existing_medical_recipe_visit.is_active = False
                session.add(existing_medical_recipe_visit)
            else:
                session.delete(existing_medical_recipe_visit)

            session.commit()
    