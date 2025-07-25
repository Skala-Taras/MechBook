from datetime import datetime, date
from typing import List
from fastapi import Depends
from sqlalchemy.orm import Session

from app.interfaces.repair_repository import IRepairRepository
from app.interfaces.repair_service import IRepairService
from app.repositories.repair_repository import RepairRepository
from app.dependencies.db import get_db
from app.schemas.repair import RepairCreate, RepairEditData, RepairExtendedInfo, RepairBasicInfo
from app.models.repairs import Repairs

class RepairService(IRepairService):
    
    def __init__(self, repair_repo: IRepairRepository = Depends(RepairRepository), db: Session = Depends(get_db)):
        self.repair_repo = repair_repo
        self.db = db
    
    @staticmethod
    def __validate_corect_result(repair: Repairs | bool | None) -> None:
        # Check if repair_id which was given is valid, if not raise error
        if not repair:
            raise ValueError("Repair not found")

    def add_repair(self, vehicle_id: int, data: RepairCreate) -> RepairExtendedInfo:
        repair_data_with_vehicle = data.dict()
        repair_data_with_vehicle['vehicle_id'] = vehicle_id
        
        new_repair = self.repair_repo.create_repair(self.db, RepairCreate(**repair_data_with_vehicle))
        return RepairExtendedInfo.model_validate(new_repair)

    def get_repair_details(self, repair_id: int) -> RepairExtendedInfo:
        repair = self.repair_repo.get_repair_by_id(self.db, repair_id)
        self.__validate_corect_result(repair)
        
        repair.last_seen = datetime.utcnow()
        self.db.commit()
        
        return RepairExtendedInfo.from_orm(repair)

    def get_all_repairs_for_vehicle(
        self,
        vehicle_id: int,
        page: int,
        size: int,        
    ) -> List[RepairBasicInfo]:
        repairs = self.repair_repo.get_repair_details(self.db, vehicle_id, page, size)
        return [RepairBasicInfo.from_orm(r) for r in repairs]

    def edit_repair_data(self, repair_id: int, data: RepairEditData):
        updated_repair = self.repair_repo.update_repair(self.db, repair_id, data)
        self.__validate_corect_result(updated_repair)
        
        updated_repair.last_seen = datetime.utcnow()
        self.db.commit()

    def delete_repair(self, repair_id: int):
        was_deleted = self.repair_repo.delete_repair(self.db, repair_id)
        self.__validate_corect_result(was_deleted)

