from datetime import datetime

from fastapi.params import Depends
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.dependencies.db import get_db
from app.interfaces.repair_repository import IRepairRepository
from app.models.repairs import Repairs
from app.schemas.repair import RepairCreate, RepairEditData

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

    def get_repair_by_id(self, repair_id: int) -> Optional[Repairs]:
        return self.db.query(Repairs).options(joinedload(Repairs.vehicle)).filter(Repairs.id == repair_id).first()

    def find_repairs_for_vehicle(self, vehicle_id: int, page: int, size: int) -> List[Repairs]:
        offset = (page - 1) * size
        return self.db.query(Repairs)\
            .filter(Repairs.vehicle_id == vehicle_id)\
            .order_by(desc(Repairs.repair_date))\
            .offset(offset)\
            .limit(size)\
            .all()

    def update_repair(self, repair_id: int, data: dict) -> Optional[Repairs]:
        repair = self.db.query(Repairs).filter(Repairs.id == repair_id).first()
        if not repair:
            return None
        
        for key, value in data.items():
            setattr(repair, key, value)
        
        self.db.commit()
        self.db.refresh(repair)
        return repair

    def delete_repair(self, repair_id: int) -> bool:
        deleted_count = self.db.query(Repairs).filter(Repairs.id == repair_id).delete(synchronize_session=False)
        self.db.commit()
        return deleted_count > 0

