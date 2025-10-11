from datetime import datetime

from fastapi.params import Depends
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.dependencies.db import get_db
from app.interfaces.repair_repository import IRepairRepository
from app.models.repairs import Repairs

class RepairRepository(IRepairRepository):
    """
    DAO - data access object
    """
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def update_last_seen_column_in_repair(self, repair: Repairs):
        repair.last_seen = datetime.utcnow()
        self.db.commit()
        self.db.refresh(repair)

    def create_repair(self, data: dict) -> Repairs:
        repair = Repairs(**data)
        self.db.add(repair)
        self.db.commit()
        self.db.refresh(repair)
        return repair

    def get_repair_by_id(self, repair_id: int, mechanic_id: int = None) -> Optional[Repairs]:
        query = self.db.query(Repairs).options(joinedload(Repairs.vehicle)).filter(Repairs.id == repair_id)
        if mechanic_id is not None:
            # Join through vehicle -> client to filter by mechanic_id
            from app.models.vehicles import Vehicles
            from app.models.clients import Clients
            query = query.join(Vehicles).join(Clients).filter(Clients.mechanic_id == mechanic_id)
        return query.first()

    def find_repairs_for_vehicle(self, vehicle_id: int, page: int, size: int, mechanic_id: int = None) -> List[Repairs]:
        offset = (page - 1) * size
        query = self.db.query(Repairs).filter(Repairs.vehicle_id == vehicle_id)
        
        if mechanic_id is not None:
            # Verify the vehicle belongs to this mechanic's client
            from app.models.vehicles import Vehicles
            from app.models.clients import Clients
            query = query.join(Vehicles).join(Clients).filter(Clients.mechanic_id == mechanic_id)
        
        return query.order_by(desc(Repairs.repair_date)).offset(offset).limit(size).all()

    def update_repair(self, repair_id: int, data: dict, mechanic_id: int = None) -> Optional[Repairs]:
        repair = self.get_repair_by_id(repair_id, mechanic_id)
        if not repair:
            return None
        
        for key, value in data.items():
            setattr(repair, key, value)
        
        self.db.commit()
        self.db.refresh(repair)
        return repair

    def delete_repair(self, repair_id: int, mechanic_id: int = None) -> bool:
        repair = self.get_repair_by_id(repair_id, mechanic_id)
        if not repair:
            return False
        
        # Use ORM delete
        self.db.delete(repair)
        self.db.commit()
        return True

