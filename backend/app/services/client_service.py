from typing import Optional
from fastapi import Depends
import logging

from app.interfaces.client_repository import IClientRepository
from app.interfaces.client_service import IClientService
from app.repositories.client_repository import ClientRepository
from app.schemas.client import ClientCreate, ClientUpdate, ClientExtendedInfo
from app.services.search_engine_service import search_service
from app.schemas.vehicle import VehicleBasicInfoForClient

class ClientService(IClientService):

    def __init__(self, client_repo: IClientRepository = Depends(ClientRepository)):
        self.client_repo = client_repo
        self._logger = logging.getLogger(__name__)

    def __validate_result(self, result: bool | None) -> None:
        if not result:
            raise ValueError("Client not found")

    def create_new_client(self, client_data: ClientCreate, mechanic_id: int) -> ClientExtendedInfo:
        client_dict = client_data.dict()
        client_dict['mechanic_id'] = mechanic_id

        # Check for duplicates before creating (only within this mechanic's clients)
        if self.client_repo.get_client_by_name_and_last_name(client_dict['name'], client_dict['last_name'], mechanic_id):
            raise ValueError("Client with this name and last name already exists.")
        
        if client_dict.get('phone') and self.client_repo.get_client_by_phone(client_dict['phone'], mechanic_id):
            raise ValueError("Client with this phone number already exists.")
        
    
        if client_dict.get('pesel'):
            all_clients = self.client_repo.get_all_clients(mechanic_id)
            for existing_client in all_clients:
                if existing_client.pesel and existing_client.pesel == client_dict['pesel']:
                    raise ValueError("Client with this pesel already exists.")
        
        new_client = self.client_repo.create_client(client_dict)
        try:
            search_service.index_client(new_client)
        except Exception:
            # Do not fail the request if search indexing is unavailable
            self._logger.exception("Failed to index client in Elasticsearch")
        
        return ClientExtendedInfo.model_validate(new_client)

    def get_client_details(self, client_id: int, mechanic_id: int) -> Optional[ClientExtendedInfo]:
        client = self.client_repo.get_client_by_id(client_id, mechanic_id)
        self.__validate_result(client)
        
        print(f"SERVICE LAYER: Fetched client {client.id}. PESEL is '{client.pesel}' (decrypted).")
        
        return ClientExtendedInfo.model_validate(client)

    def update_client_details(self, client_id: int, client_data: ClientUpdate, mechanic_id: int) -> Optional[ClientExtendedInfo]:
        updated_client = self.client_repo.update_client(client_id, client_data, mechanic_id)
        self.__validate_result(updated_client)
        
        try:
            search_service.index_client(updated_client)
        except Exception:
            self._logger.exception("Failed to re-index client after update")
        return ClientExtendedInfo.model_validate(updated_client)

    def remove_client(self, client_id: int, mechanic_id: int) -> None:
        was_deleted = self.client_repo.delete_client(client_id, mechanic_id)
        self.__validate_result(was_deleted)
        try:
            # Delete client and all their vehicles from Elasticsearch
            search_service.delete_client_and_vehicles(client_id)
        except Exception:
            self._logger.exception("Failed to remove client and vehicles from Elasticsearch index")

    def get_client_vehicles(self, client_id: int, page: int, size: int, mechanic_id: int) -> list[VehicleBasicInfoForClient]:
        client = self.client_repo.get_client_by_id(client_id, mechanic_id)
        self.__validate_result(client)
        vehicles = self.client_repo.get_client_vehicles(client_id, page, size, mechanic_id)
        return [VehicleBasicInfoForClient.model_validate(vehicle) for vehicle in vehicles]
    
    def list_all_clients(self, page: int, size: int, mechanic_id: int) -> list[ClientExtendedInfo]:
        """
        Get all clients for a mechanic with pagination.
        Returns list of clients ordered by newest first.
        """
        clients = self.client_repo.get_all_clients_paginated(page, size, mechanic_id)
        return [ClientExtendedInfo.model_validate(client) for client in clients]
    
    def count_all_clients(self, mechanic_id: int) -> int:
        """
        Count total number of clients for a mechanic.
        """
        return self.client_repo.count_clients(mechanic_id)
