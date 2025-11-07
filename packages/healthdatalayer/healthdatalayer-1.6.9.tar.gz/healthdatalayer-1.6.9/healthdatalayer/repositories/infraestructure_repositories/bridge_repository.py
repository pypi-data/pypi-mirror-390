from typing import Optional, List
from uuid import UUID
from sqlmodel import select
from sqlalchemy.orm import selectinload,joinedload

from healthdatalayer.models import BridgeAreaFloorBranch
from healthdatalayer.models import Branch
from healthdatalayer.config.db import engines, get_session

class BridgeAreaFloorBranchRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")

    def create_command(self, bridge: BridgeAreaFloorBranch) -> BridgeAreaFloorBranch:
        with get_session(self.tenant) as session:
            session.add(bridge)
            session.commit()
            session.refresh(bridge)
            return bridge

    def get_by_id_command(self, bridge_id: UUID, load_related: bool = False) -> Optional[BridgeAreaFloorBranch]:
        with get_session(self.tenant) as session:
            statement = select(BridgeAreaFloorBranch).where(BridgeAreaFloorBranch.bridge_area_floor_branch_id == bridge_id)
            if load_related:
                statement = statement.options(
                    selectinload(BridgeAreaFloorBranch.branch).selectinload(Branch.system),
                    selectinload(BridgeAreaFloorBranch.area),
                    selectinload(BridgeAreaFloorBranch.floor),
                    selectinload(BridgeAreaFloorBranch.room)
                )
            bridge = session.exec(statement).first()
            
                    
            return bridge

    def get_all_command(self, active_only: bool = True,load_related: bool = False) -> List[BridgeAreaFloorBranch]:
        with get_session(self.tenant) as session:
            statement = select(BridgeAreaFloorBranch)
            if active_only:
                statement = statement.where(BridgeAreaFloorBranch.is_active == True)
            #results = session.exec(statement).all()
            
            if load_related:
                statement = statement.options(
                    selectinload(BridgeAreaFloorBranch.branch).selectinload(Branch.system),
                    selectinload(BridgeAreaFloorBranch.area),
                    selectinload(BridgeAreaFloorBranch.floor),
                    selectinload(BridgeAreaFloorBranch.room)
                )
               
            results = session.exec(statement).all()
            return results
    
    def update_command(self, bridge: BridgeAreaFloorBranch) -> BridgeAreaFloorBranch:
        with get_session(self.tenant) as session:
            existing_bridge = session.get(BridgeAreaFloorBranch, bridge.bridge_area_floor_branch_id)
            if not existing_bridge:
                raise ValueError(f"BridgeAreaFloorBranch with id {bridge.bridge_area_floor_branch_id} does not exist")
            
            for key, value in bridge.dict(exclude_unset=True).items():
                setattr(existing_bridge, key, value)
            
            bd_bridge =  session.merge(existing_bridge)
            session.commit()
            session.refresh(bd_bridge)
            return bd_bridge

    def delete_command(self, bridge_id: UUID, soft_delete: bool = False) -> None:
        with get_session(self.tenant) as session:
            existing_bridge = session.get(BridgeAreaFloorBranch, bridge_id)
            if not existing_bridge:
                raise ValueError(f"BridgeAreaFloorBranch with id {bridge_id} does not exist")

            if soft_delete:
                existing_bridge.is_active = False
                session.add(existing_bridge)
            else:
                session.delete(existing_bridge)

            session.commit()