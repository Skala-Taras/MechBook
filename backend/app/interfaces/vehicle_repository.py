from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.vehicles import Vehicles

class IVehicleRepository(ABC):
    #Depends on get_db
    @abstractmethod
    def update_last_view_column_in_vehicles(self, vehicle: Vehicles) -> None:
        pass

    @abstractmethod
    def create_vehicle(self, vehicle_data: dict) -> Vehicles:
        pass

    @abstractmethod
    def get_vehicle_by_id(self, vehicle_id: int) -> Optional[Vehicles]:
        pass

    @abstractmethod
    def get_recently_viewed_vehicles(self, limit: int = 5) -> List[Vehicles]:
        pass

    @abstractmethod
    def update_vehicle(self, vehicle_id: int, data: dict) -> Optional[Vehicles]:
        pass

    @abstractmethod
    def delete_vehicle(self, vehicle_id: int) -> bool:
        pass