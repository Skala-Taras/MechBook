from abc import ABC, abstractmethod
from typing import Optional
from app.models.clients import Clients
from app.schemas.client import ClientUpdate
from app.models.vehicles import Vehicles

class IClientRepository(ABC):
    
    @abstractmethod
    def create_client(self, client_data: dict) -> Clients:
        pass

    @abstractmethod
    def get_client_by_id(self, client_id: int) -> Optional[Clients]:
        pass

    @abstractmethod
    def get_client_by_phone(self, phone: str) -> Optional[Clients]:
        pass

    @abstractmethod
    def get_client_by_pesel(self, pesel: str) -> Optional[Clients]:
        pass

    @abstractmethod
    def get_client_by_name_and_last_name(self, name: str, last_name: str) -> Optional[Clients]:
        pass

    @abstractmethod
    def update_client(self, client_id: int, client_data: ClientUpdate) -> Optional[Clients]:
        pass

    @abstractmethod
    def delete_client(self, client_id: int) -> bool:
        pass
    
    @abstractmethod
    def get_client_vehicles(self, client_id: int, page: int, size: int) -> list[Vehicles]:
        pass