from datetime import datetime

from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.interfaces.repair_repository import IRepairRepository
from app.models.repairs import Repairs
from app.schemas.repair import RepairCreate, RepairEditData


class RepairRepository(IRepairRepository):
    """
    DAO - data access object
    """
    def create_repair(self, db: Session, data: RepairCreate) -> Repairs:
        repair = Repairs(**data.dict())
        db.add(repair)
        db.commit()
        db.refresh(repair)
        return repair

    def get_repair_details(self, db: Session, repair_id: int) -> Optional[Repairs]:
        return db.query(Repairs).options(joinedload(Repairs.vehicle)).filter(Repairs.id == repair_id).first()

    def get_repair_details(self, db: Session, vehicle_id: int, page: int, size: int) -> List[Repairs]:
        offset = (page - 1) * size
        return db.query(Repairs)\
            .filter(Repairs.vehicle_id == vehicle_id)\
            .order_by(desc(Repairs.repair_date))\
            .offset(offset)\
            .limit(size)\
            .all()

    def update_repair(self, db: Session, repair_id: int, data: RepairEditData) -> Optional[Repairs]:
        repair = db.query(Repairs).filter(Repairs.id == repair_id).first()
        if not repair:
            return None
        
        for key, value in data.dict(exclude_unset=True).items():
            setattr(repair, key, value)
        
        db.commit()
        db.refresh(repair)
        return repair

    def delete_repair(self, db: Session, repair_id: int) -> bool:
        deleted_count = db.query(Repairs).filter(Repairs.id == repair_id).delete(synchronize_session=False)
        db.commit()
        return deleted_count > 0

