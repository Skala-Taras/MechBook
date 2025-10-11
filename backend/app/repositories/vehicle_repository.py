from datetime import datetime
from typing import List, Optional

from fastapi.params import Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from fastapi import HTTPException

from app.dependencies.db import get_db
from app.interfaces.vehicle_repository import IVehicleRepository
from app.models.vehicles import Vehicles
from app.core.security import vin_fingerprint

class VehicleRepository(IVehicleRepository):
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def update_last_view_column_in_vehicles(self, vehicle: Vehicles) -> None:
        vehicle.last_view_data = datetime.utcnow()
        self.db.commit()
        self.db.refresh(vehicle)

    def create_vehicle(self, vehicle_data: dict, mechanic_id: int = None) -> Vehicles:
        vin = vehicle_data.get("vin")
        if vin:
            # Create fingerprint for duplicate detection
            fingerprint = vin_fingerprint(vin)
            
            # Check for duplicate VIN per mechanic
            if mechanic_id is not None:
                from app.models.clients import Clients
                existing_vehicle = self.db.query(Vehicles)\
                    .join(Clients)\
                    .filter(Vehicles.vin_hash == fingerprint, Clients.mechanic_id == mechanic_id)\
                    .first()
                if existing_vehicle:
                    raise HTTPException(status_code=409, detail="Vehicle with this VIN already exists.")
            else:
                # Fallback to global check if mechanic_id not provided
                if self.db.query(Vehicles).filter(Vehicles.vin_hash == fingerprint).first():
                    raise HTTPException(status_code=409, detail="Vehicle with this VIN already exists.")
            
            vehicle_data["vin_hash"] = fingerprint
        
        new_vehicle = Vehicles(**vehicle_data)
        self.db.add(new_vehicle)
        self.db.commit()
        self.db.refresh(new_vehicle)
        return new_vehicle

    def get_vehicle_by_id(self, vehicle_id: int, mechanic_id: int = None) -> Optional[Vehicles]:
        query = self.db.query(Vehicles).options(joinedload(Vehicles.client)).filter(Vehicles.id == vehicle_id)
        if mechanic_id is not None:
            # Join with clients table to filter by mechanic_id
            from app.models.clients import Clients
            query = query.join(Clients).filter(Clients.mechanic_id == mechanic_id)
        return query.first()

    def get_recently_viewed_vehicles(self, limit: int, page: int, mechanic_id: int = None) -> List[Vehicles]:
        query = self.db.query(Vehicles)
        if mechanic_id is not None:
            from app.models.clients import Clients
            query = query.join(Clients).filter(Clients.mechanic_id == mechanic_id)
        return query.order_by(desc(Vehicles.last_view_data)).offset((page - 1) * limit).limit(limit).all()

    def update_vehicle(self, vehicle_id: int, data: dict, mechanic_id: int = None) -> Optional[Vehicles]:
        vehicle = self.get_vehicle_by_id(vehicle_id, mechanic_id)
        if not vehicle:
            return None
        
        # If VIN is being updated, create new fingerprint
        if "vin" in data and data["vin"]:
            fingerprint = vin_fingerprint(data["vin"])
            data["vin_hash"] = fingerprint
        
        for key, value in data.items():
            setattr(vehicle, key, value)
        
        self.db.commit()
        self.db.refresh(vehicle)
        return vehicle

    def delete_vehicle(self, vehicle_id: int, mechanic_id: int = None) -> bool:
        # With cascade="all, delete-orphan" in the model, deleting the vehicle
        # will automatically delete all associated repairs
        vehicle = self.get_vehicle_by_id(vehicle_id, mechanic_id)
        if not vehicle:
            return False
        
        deleted_count = self.db.query(Vehicles).filter(Vehicles.id == vehicle_id).delete(synchronize_session=False)
        self.db.commit()
        return deleted_count > 0 