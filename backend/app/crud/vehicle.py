from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, desc

from fastapi import HTTPException

from app.models import Clients
from app.models.vehicles import Vehicles
from app.schemas.vehicle import VehicleCreate


def create_vehicle(db: Session, vehicle_data: dict):
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

    return new_vehicle

def get_extended_vehicle_and_client_data(db: Session, vehicle_id: int) -> Vehicles:
    """

    :param db:
    :param vehicle_id:
    :return: Vehicles
    """
    return db.query(Vehicles).options(joinedload(Vehicles.client)).filter(Vehicles.id == vehicle_id).first()


def get_recently_used_vehicles(db: Session) -> list[Vehicles]:
    """
    Gives 5 most recently viewed vehicles sorted by last_viewed_data (DESC)
    (viewed a car, or repairing it)

    :param db:
    :return: list of Vehicles
    """
    return db.query(Vehicles).order_by(desc(Vehicles.last_view_data)).limit(5).all()