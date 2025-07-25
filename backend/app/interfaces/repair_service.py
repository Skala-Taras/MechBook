from abc import ABC, abstractmethod
from typing import List
from app.schemas.repair import RepairCreate, RepairEditData, RepairExtendedInfo, RepairBasicInfo
from app.models.repairs import Repairs

class IRepairService(ABC):

    @abstractmethod
    def add_repair(self, vehicle_id: int, data: RepairCreate) -> int:
        pass

    @abstractmethod
    def get_repair_details(self, repair_id: int) -> RepairExtendedInfo:
        pass

    @abstractmethod
    def get_recent_repairs(self) -> List[RepairBasicInfo]:
        pass

    @abstractmethod
    def edit_repair_data(self, repair_id: int, repair_data: RepairEditData) -> Repairs:
        pass

    @abstractmethod
    def delete_repair(self, repair_id: int) -> bool:
        pass