from abc import ABC, abstractmethod
from typing import Optional
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.interfaces.client_repository import IClientRepository
from app.models.clients import Clients
from app.schemas.client import ClientUpdate


class ClientRepository(IClientRepository):

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create_client(self, client_data: dict) -> Clients:
        # Check for phone number uniqueness
        phone = client_data.get("phone")
        if phone and self.db.query(Clients).filter(Clients.phone == phone).first():
            raise HTTPException(status_code=409, detail="Client with this phone number already exists.")

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
        for key, value in update_data.items():
            setattr(client, key, value)
            
        self.db.commit()
        self.db.refresh(client)
        return client

    def delete_client(self, client_id: int) -> bool:
        deleted_count = self.db.query(Clients).filter(Clients.id == client_id).delete(synchronize_session=False)
        self.db.commit()
        return deleted_count > 0
