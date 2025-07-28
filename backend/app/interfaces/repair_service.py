from abc import ABC, abstractmethod
from typing import List
from app.schemas.repair import RepairCreate, RepairEditData, RepairExtendedInfo, RepairBasicInfo
from app.models.repairs import Repairs

class IRepairService(ABC):

    @abstractmethod
    def log_new_repair_for_vehicle(self, vehicle_id: int, data: RepairCreate) -> int:
        pass

    @abstractmethod
    def get_repair_details(self, repair_id: int) -> RepairExtendedInfo:
        pass

    @abstractmethod
    def list_repairs_for_vehicle(selfself, vehicle_id: int, page: int, size: int) -> List[RepairBasicInfo]:
        pass

    @abstractmethod
    def update_repair_information(self, repair_id: int, data: RepairEditData) -> RepairExtendedInfo:
        pass

    @abstractmethod
    def delete_repair(self, repair_id: int) -> None:
        pass