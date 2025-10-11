from abc import ABC, abstractmethod
from typing import List
from app.schemas.repair import RepairCreate, RepairEditData, RepairExtendedInfo, RepairBasicInfo

class IRepairService(ABC):

    @abstractmethod
    def log_new_repair_for_vehicle(self, vehicle_id: int, data: RepairCreate, mechanic_id: int) -> RepairExtendedInfo:
        pass

    @abstractmethod
    def get_repair_details(self, repair_id: int, mechanic_id: int) -> RepairExtendedInfo:
        pass

    @abstractmethod
    def list_repairs_for_vehicle(self, vehicle_id: int, page: int, size: int, mechanic_id: int) -> List[RepairBasicInfo]:
        pass

    @abstractmethod
    def update_repair_information(self, repair_id: int, data: RepairEditData, mechanic_id: int):
        pass

    @abstractmethod
    def delete_repair(self, repair_id: int, mechanic_id: int):
        pass