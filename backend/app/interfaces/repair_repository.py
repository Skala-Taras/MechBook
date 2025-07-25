from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.repairs import Repairs
from app.schemas.repair import RepairCreate, RepairEditData

class IRepairRepository(ABC):

    @abstractmethod
    def create_repair(self, data: RepairCreate) -> Repairs:
        pass

    @abstractmethod
    def get_repair_details(self, repair_id: int) -> Optional[Repairs]:
        pass
    
    # @abstractmethod
    # def get_all_repairs_for_vehicle(self, vehicle_id: int, page: int, size: int) -> List[Repairs]:
    #     pass

    @abstractmethod
    def update_repair(self, repair_id: int, data: RepairEditData) -> Optional[Repairs]:
        pass

    @abstractmethod
    def delete_repair(self, repair_id: int) -> bool:
        pass