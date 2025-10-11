from abc import ABC, abstractmethod
from typing import List, Optional
from app.schemas.vehicle import VehicleCreate, VehicleEditData, VehicleExtendedInfo, VehicleBasicInfo

class IVehicleService(ABC):

    @abstractmethod
    def register_new_vehicle(self, data: VehicleCreate, mechanic_id: int) -> int:
        pass

    @abstractmethod
    def get_vehicle_details(self, vehicle_id: int, mechanic_id: int) -> VehicleExtendedInfo:
        pass

    @abstractmethod
    def list_recently_viewed_vehicles(self, page: int, size: int, mechanic_id: int) -> Optional[List[VehicleBasicInfo]]:
        pass

    @abstractmethod
    def update_vehicle_information(self, vehicle_id: int, data: VehicleEditData, mechanic_id: int) -> VehicleExtendedInfo:
        pass

    @abstractmethod
    def delete_vehicle(self, vehicle_id: int, mechanic_id: int) -> None:
        pass
    
    @abstractmethod
    def list_all_vehicles(self, page: int, size: int, mechanic_id: int) -> List[VehicleBasicInfo]:
        pass
    
    @abstractmethod
    def count_all_vehicles(self, mechanic_id: int) -> int:
        pass