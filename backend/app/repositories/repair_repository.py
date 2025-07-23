from datetime import datetime
from typing import Any

from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from .interfaces.repair_repository_interface import IRepairRepository
from ..models import Vehicles, Repairs
from ..schemas.repair import RepairEditData, RepairBasicInfo, RepairExtendedInfo


class RepairRepository(IRepairRepository):
    """
    DAO - data access object
    """
    def __init__(self, db_session: Session):
        self.db = db_session

    def __update_last_view_time(self, repair_object: Repairs) -> None:
        repair_object.last_seen = datetime.utcnow()
        self.db.commit()

    def __get_repair_object(self, repair_id: int) -> Repairs | None:
        obj = self.db.query(Repairs).filter(Repairs.id == repair_id).first()
        return obj

    def add(self, data: dict) -> int:
        repair = Repairs(**data)
        self.db.add(repair)
        self.__update_last_view_time(repair)
        self.db.refresh(repair)
        return repair.id

    def edit(self, data: dict) -> bool:
        repair_id = data.get("repair_id")
        repair = self.__get_repair_object(repair_id)
        if not repair:
            return False
        for key, value in data.items():
            setattr(repair, key, value)
        self.__update_last_view_time(repair)
        self.db.refresh(repair)
        return True

    def get_data_by_id(self, repair_id: int):
        repair = self.__get_repair_object(repair_id)
        if not repair: return None
        result = self.db.query(Repairs).options(joinedload(Repairs.vehicle)).filter(Repairs.id == repair_id).first()
        self.__update_last_view_time(repair)
        self.db.refresh(repair)
        return result

    def recently(self) -> list[RepairBasicInfo]:
        return self.db.query(Repairs).order_by(desc(Repairs.last_seen)).limit(5).all()

    def delete(self, repair_id: int) -> bool:
        repair = self.__get_repair_object(repair_id)
        if not repair: return False
        self.db.delete(repair)
        self.db.commit()
        return True

