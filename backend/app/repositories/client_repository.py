from typing import Optional
from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.interfaces.client_repository import IClientRepository
from app.models.clients import Clients
from app.models.vehicles import Vehicles
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

    def get_client_by_id(self, client_id: int, mechanic_id: int = None) -> Optional[Clients]:
        query = self.db.query(Clients).filter(Clients.id == client_id)
        if mechanic_id is not None:
            query = query.filter(Clients.mechanic_id == mechanic_id)
        return query.first()

    def update_client(self, client_id: int, client_data: ClientUpdate, mechanic_id: int) -> Optional[Clients]:
        client = self.get_client_by_id(client_id, mechanic_id)
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

    def delete_client(self, client_id: int, mechanic_id: int) -> bool:
        # With cascade="all, delete-orphan" in the model, deleting the client
        # will automatically delete all associated vehicles and their repairs
        client = self.get_client_by_id(client_id, mechanic_id)
        if not client:
            return False
        
        # Use ORM delete to trigger cascade delete
        self.db.delete(client)
        self.db.commit()
        return True

    def get_client_by_name_and_last_name(self, name: str, last_name: str, mechanic_id: int = None) -> Optional[Clients]:
        # Case-insensitive search for duplicate checking
        query = self.db.query(Clients).filter(
            Clients.name.ilike(name.strip()), 
            Clients.last_name.ilike(last_name.strip())
        )
        if mechanic_id is not None:
            query = query.filter(Clients.mechanic_id == mechanic_id)
        return query.first()

    def get_client_by_phone(self, phone: str, mechanic_id: int = None) -> Optional[Clients]:
        if not phone:
            return None
        query = self.db.query(Clients).filter(Clients.phone == phone)
        if mechanic_id is not None:
            query = query.filter(Clients.mechanic_id == mechanic_id)
        return query.first()

    def get_client_by_pesel(self, pesel: str, mechanic_id: int = None) -> Optional[Clients]:
        if not pesel:
            return None
        query = self.db.query(Clients).filter(Clients.pesel == pesel)
        if mechanic_id is not None:
            query = query.filter(Clients.mechanic_id == mechanic_id)
        return query.first()
    
    def get_all_clients(self, mechanic_id: int = None) -> list[Clients]:
        query = self.db.query(Clients)
        if mechanic_id is not None:
            query = query.filter(Clients.mechanic_id == mechanic_id)
        return query.all()
    
    def get_client_vehicles(self, client_id: int, page: int, size: int, mechanic_id: int = None) -> list[Vehicles]:
        # First verify the client belongs to this mechanic
        if mechanic_id is not None:
            client = self.get_client_by_id(client_id, mechanic_id)
            if not client:
                return []
        return self.db.query(Vehicles).filter(Vehicles.client_id == client_id).offset((page - 1) * size).limit(size).all()