from datetime import datetime
from sqlalchemy.orm import Session

from fastapi import HTTPException
from app.models.vehicles import Vehicles
from app.schemas.vehicle import VehicleCreate


def create_vehicle(db: Session, vehicle_data: dict) -> int:
    vin = vehicle_data.get("vin")

    if vin:
        existing_vehicle = db.query(Vehicles).filter(Vehicles.vin == vin).first()
        if existing_vehicle:
            raise HTTPException(
                status_code=409,  # Conflict
                detail="Vehicle with this VIN already exists."
            )
    new_vehicle = Vehicles(**vehicle_data)
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)
    return new_vehicle.id