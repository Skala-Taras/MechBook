from typing import List
from fastapi import Depends

from app.interfaces.repair_repository import IRepairRepository
from app.interfaces.repair_service import IRepairService
from app.repositories.repair_repository import RepairRepository
from app.schemas.repair import RepairCreate, RepairEditData, RepairExtendedInfo, RepairBasicInfo
from app.models.repairs import Repairs

class RepairService(IRepairService):
    
    def __init__(self, repair_repo: IRepairRepository = Depends(RepairRepository)):
        self.repair_repo = repair_repo
    
    @staticmethod
    def __validate_correct_result(repair: Repairs | bool | None) -> None:
        # Check if repair_id which was given is valid, if not raise ValueError
        if not repair:
            raise ValueError("Repair not found")

    def log_new_repair_for_vehicle(self, vehicle_id: int, data: RepairCreate) -> RepairExtendedInfo:
        repair_data_with_vehicle = data.dict()
        repair_data_with_vehicle['vehicle_id'] = vehicle_id
        
        new_repair = self.repair_repo.create_repair(repair_data_with_vehicle)
        return RepairExtendedInfo.model_validate(new_repair)

    def get_repair_details(self, repair_id: int) -> RepairExtendedInfo:
        repair = self.repair_repo.get_repair_by_id(repair_id)
        self.__validate_correct_result(repair)
        self.repair_repo.update_last_seen_column_in_repair(repair)
        return RepairExtendedInfo.model_validate(repair)

    def list_repairs_for_vehicle(
        self,
        vehicle_id: int,
        page: int,
        size: int,        
    ) -> List[RepairBasicInfo]:
        repairs = self.repair_repo.find_repairs_for_vehicle(vehicle_id, page, size)
        return [RepairBasicInfo.model_validate(r) for r in repairs]

    def update_repair_information(self, repair_id: int, data: RepairEditData):
        updated_repair = self.repair_repo.update_repair(repair_id, data.dict(exclude_unset=True))
        # Give repository only data that needed fild without None key
        self.__validate_correct_result(updated_repair)
        self.repair_repo.update_last_seen_column_in_repair(updated_repair)

    def delete_repair(self, repair_id: int):
        was_deleted = self.repair_repo.delete_repair(repair_id)
        self.__validate_correct_result(was_deleted)

