from typing import Optional
from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.interfaces.client_repository import IClientRepository
from app.models.clients import Clients
from app.schemas.client import ClientUpdate


class ClientRepository(IClientRepository):

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create_client(self, client_data: dict) -> Clients:
        # Format names properly: "taras ska" -> "Taras Ska"
        if "name" in client_data and client_data["name"]:
            client_data["name"] = client_data["name"].strip().title()
        if "last_name" in client_data and client_data["last_name"]:
            client_data["last_name"] = client_data["last_name"].strip().title()
            
        new_client = Clients(**client_data)
        self.db.add(new_client)
        self.db.commit()
        self.db.refresh(new_client)
        return new_client

    def get_client_by_id(self, client_id: int) -> Optional[Clients]:
        return self.db.query(Clients).filter(Clients.id == client_id).first()

    def update_client(self, client_id: int, client_data: ClientUpdate) -> Optional[Clients]:
        client = self.get_client_by_id(client_id)
        if not client:
            return None
        
        update_data = client_data.dict(exclude_unset=True)
        
        # Format names properly: "taras ska" -> "Taras Ska"
        if "name" in update_data and update_data["name"]:
            update_data["name"] = update_data["name"].strip().title()
        if "last_name" in update_data and update_data["last_name"]:
            update_data["last_name"] = update_data["last_name"].strip().title()
        
        for key, value in update_data.items():
            setattr(client, key, value)
            
        self.db.commit()
        self.db.refresh(client)
        return client

    def delete_client(self, client_id: int) -> bool:
        deleted_count = self.db.query(Clients).filter(Clients.id == client_id).delete(synchronize_session=False)
        self.db.commit()
        return deleted_count > 0

    def get_client_by_name_and_last_name(self, name: str, last_name: str) -> Optional[Clients]:
        # Case-insensitive search for duplicate checking
        return self.db.query(Clients).filter(
            Clients.name.ilike(name.strip()), 
            Clients.last_name.ilike(last_name.strip())
        ).first()

    def get_client_by_phone(self, phone: str) -> Optional[Clients]:
        if not phone:
            return None
        return self.db.query(Clients).filter(Clients.phone == phone).first()

    def get_client_by_pesel(self, pesel: str) -> Optional[Clients]:
        if not pesel:
            return None
        return self.db.query(Clients).filter(Clients.pesel == pesel).first()
    
    def get_all_clients(self) -> list[Clients]:
        return self.db.query(Clients).all()