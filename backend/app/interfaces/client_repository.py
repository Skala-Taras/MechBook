from abc import ABC, abstractmethod
from typing import Optional
from app.models.clients import Clients
from app.schemas.client import ClientUpdate

class IClientRepository(ABC):
    
    @abstractmethod
    def create_client(self, client_data: dict) -> Clients:
        pass

    @abstractmethod
    def get_client_by_id(self, client_id: int) -> Optional[Clients]:
        pass

    @abstractmethod
    def update_client(self, client_id: int, client_data: ClientUpdate) -> Optional[Clients]:
        pass

    @abstractmethod
    def delete_client(self, client_id: int) -> bool:
        pass
