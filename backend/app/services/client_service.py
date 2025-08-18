from typing import Optional
from fastapi import Depends, HTTPException
import logging

from app.interfaces.client_repository import IClientRepository
from app.interfaces.client_service import IClientService
from app.repositories.client_repository import ClientRepository
from app.schemas.client import ClientCreate, ClientUpdate, ClientExtendedInfo
from app.services.search_engine_service import search_service

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

        # Check for duplicates before creating
        if self.client_repo.get_client_by_name_and_last_name(client_dict['name'], client_dict['last_name']):
            raise HTTPException(status_code=409, detail="Client with this name and last name already exists.")
        
        if client_dict.get('phone') and self.client_repo.get_client_by_phone(client_dict['phone']):
            raise HTTPException(status_code=409, detail="Client with this phone number already exists.")
        
        if client_dict.get('pesel') and self.client_repo.get_client_by_pesel(client_dict['pesel']):
            raise HTTPException(status_code=409, detail="Client with this pesel already exists.")
        
        new_client = self.client_repo.create_client(client_dict)
        try:
            search_service.index_client(new_client)
        except Exception:
            # Do not fail the request if search indexing is unavailable
            self._logger.exception("Failed to index client in Elasticsearch")
        
        return ClientExtendedInfo.model_validate(new_client)

    def get_client_details(self, client_id: int) -> Optional[ClientExtendedInfo]:
        client = self.client_repo.get_client_by_id(client_id)
        self.__validate_result(client)
        
        print(f"SERVICE LAYER: Fetched client {client.id}. PESEL is '{client.pesel}' (decrypted).")
        
        return ClientExtendedInfo.model_validate(client)

    def update_client_details(self, client_id: int, client_data: ClientUpdate) -> Optional[ClientExtendedInfo]:
        updated_client = self.client_repo.update_client(client_id, client_data)
        self.__validate_result(updated_client)
        
        try:
            search_service.index_client(updated_client)
        except Exception:
            self._logger.exception("Failed to re-index client after update")
        return ClientExtendedInfo.model_validate(updated_client)

    def remove_client(self, client_id: int) -> None:
        was_deleted = self.client_repo.delete_client(client_id)
        self.__validate_result(was_deleted)
        try:
            search_service.delete_document(f"client-{client_id}")
        except Exception:
            self._logger.exception("Failed to remove client from Elasticsearch index")
