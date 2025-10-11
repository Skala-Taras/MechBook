from abc import ABC, abstractmethod
from typing import Optional
from app.schemas.client import ClientCreate, ClientUpdate, ClientExtendedInfo
from app.schemas.vehicle import VehicleBasicInfoForClient

class IClientService(ABC):

    @abstractmethod
    def create_new_client(self, client_data: ClientCreate, mechanic_id: int) -> ClientExtendedInfo:
        pass

    @abstractmethod
    def get_client_details(self, client_id: int, mechanic_id: int) -> Optional[ClientExtendedInfo]:
        pass

    @abstractmethod
    def update_client_details(self, client_id: int, client_data: ClientUpdate, mechanic_id: int) -> Optional[ClientExtendedInfo]:
        pass

    @abstractmethod
    def remove_client(self, client_id: int, mechanic_id: int) -> None:
        pass

    @abstractmethod
    def get_client_vehicles(self, client_id: int, page: int, size: int, mechanic_id: int) -> list[VehicleBasicInfoForClient]:
        pass