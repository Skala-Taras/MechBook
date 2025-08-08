from typing import Optional
from fastapi import Depends

from app.interfaces.client_repository import IClientRepository
from app.interfaces.client_service import IClientService
from app.repositories.client_repository import ClientRepository
from app.schemas.client import ClientCreate, ClientUpdate, ClientExtendedInfo
from app.services.search_engine_service import search_service

class ClientService(IClientService):

    def __init__(self, client_repo: IClientRepository = Depends(ClientRepository)):
        self.client_repo = client_repo

    def __validate_result(self, result: bool | None) -> None:
        if not result:
            raise ValueError("Client not found")

    def create_new_client(self, client_data: ClientCreate, mechanic_id: int) -> ClientExtendedInfo:
        client_dict = client_data.dict()
        client_dict['mechanic_id'] = mechanic_id
        
        new_client = self.client_repo.create_client(client_dict)
        search_service.index_client(new_client)
        
        return ClientExtendedInfo.model_validate(new_client)

    def get_client_details(self, client_id: int) -> Optional[ClientExtendedInfo]:
        client = self.client_repo.get_client_by_id(client_id)
        self.__validate_result(client)
        
        print(f"SERVICE LAYER: Fetched client {client.id}. PESEL is '{client.pesel}' (decrypted).")
        
        return ClientExtendedInfo.model_validate(client)

    def update_client_details(self, client_id: int, client_data: ClientUpdate) -> Optional[ClientExtendedInfo]:
        updated_client = self.client_repo.update_client(client_id, client_data)
        self.__validate_result(updated_client)
        
        search_service.index_client(updated_client)
        return ClientExtendedInfo.model_validate(updated_client)

    def remove_client(self, client_id: int) -> None:
        was_deleted = self.client_repo.delete_client(client_id)
        self.__validate_result(was_deleted)
        search_service.delete_document(f"client-{client_id}")
