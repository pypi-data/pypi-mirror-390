from typing import Optional, List
from uuid import UUID
from sqlmodel import select
from sqlalchemy.orm import selectinload,joinedload
from healthdatalayer.models import MedicalDrugRecipe
from healthdatalayer.config.db import engines, get_session

class MedicalDrugRecipeRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")
    def create_command(self, medical_drug_recipe: MedicalDrugRecipe) -> MedicalDrugRecipe:
        with get_session(self.tenant) as session:
            session.add(medical_drug_recipe)
            session.commit()
            session.refresh(medical_drug_recipe)
            return medical_drug_recipe

    def get_by_id_command(self, medical_drug_recipe_id: UUID) -> Optional[MedicalDrugRecipe]:
        with get_session(self.tenant) as session:
            statement = select(MedicalDrugRecipe).where(MedicalDrugRecipe.medical_drug_recipe_id == medical_drug_recipe_id)
            return session.exec(statement).first()
        
    def list_all_command(self, active_only: bool = True)->List[MedicalDrugRecipe]:
        with get_session(self.tenant) as session:
            
            statement = select(MedicalDrugRecipe)
            if active_only:
                statement = statement.where(MedicalDrugRecipe.is_active == True)
                
            return session.exec(statement).all()
    
    def get_by_medical_recipe_visit_id_command(self, medical_recipe_visit_id: UUID,active_only: bool = True)-> List[MedicalDrugRecipe]:
        with get_session(self.tenant) as session:
            statement = select(MedicalDrugRecipe).where(MedicalDrugRecipe.medical_recipe_visit_id == medical_recipe_visit_id)
            if active_only:
                statement = statement.where(MedicalDrugRecipe.is_active == True)
                
            return session.exec(statement).all()
    
    def update_command(self, medical_drug_recipe_id: UUID, **kwargs) -> Optional[MedicalDrugRecipe]:
        with get_session(self.tenant) as session:
            db_medical_drug_recipe = session.get(MedicalDrugRecipe, medical_drug_recipe_id)
            if not db_medical_drug_recipe:
                return None
            
            for key, value in kwargs.items():
                if hasattr(db_medical_drug_recipe, key):
                    setattr(db_medical_drug_recipe, key, value)
            
            session.add(db_medical_drug_recipe)
            session.commit()
            session.refresh(db_medical_drug_recipe)
            return db_medical_drug_recipe
    
    def delete_command(self, medical_drug_recipe_id: UUID, soft_delete: bool = True) -> bool:
        with get_session(self.tenant) as session:
            statement = select(MedicalDrugRecipe).where(MedicalDrugRecipe.medical_drug_recipe_id == medical_drug_recipe_id)
            db_medical_drug_recipe = session.exec(statement).first()
            if not db_medical_drug_recipe:
                return False
            
            if soft_delete:
                db_medical_drug_recipe.is_active = False
                session.add(db_medical_drug_recipe)
            else:
                session.delete(db_medical_drug_recipe)
            
            session.commit()
            return True