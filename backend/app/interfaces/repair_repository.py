from abc import ABC, abstractmethod
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.repairs import Repairs
from app.schemas.repair import RepairCreate, RepairEditData

class IRepairRepository(ABC):
    # Depends on get_db
    @abstractmethod
    def update_last_seen_column_in_repair(self, repair: Repairs) -> None:
        pass

    @abstractmethod
    def create_repair(self, data: dict) -> Repairs:
        pass

    @abstractmethod
    def get_repair_by_id(self, repair_id: int) -> Optional[Repairs]:
        pass

    @abstractmethod
    def find_repairs_for_vehicle(self, vehicle_id: int, page: int, size: int) -> Optional[List[Repairs]]:
        pass

    @abstractmethod
    def update_repair(self, repair_id: int, data: dict) -> Optional[Repairs]:
        pass

    @abstractmethod
    def delete_repair(self, repair_id: int) -> bool:
        pass
