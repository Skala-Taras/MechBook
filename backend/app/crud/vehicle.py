from datetime import datetime

from fastapi.params import Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, desc

from fastapi import HTTPException

from app.models import Clients
from app.models.vehicles import Vehicles
from app.schemas.vehicle import VehicleCreate, VehicleEditData


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

def get_extended_vehicle_and_client_data(db: Session, vehicle_id: int):
    """
    Get joined tables Vehicles and Clients
    :param db:
    :param vehicle_id:
    :return: Joined Vehicles with CLients
    """
    result = db.query(Vehicles).options(joinedload(Vehicles.client)).filter(Vehicles.id == vehicle_id).first()
    if result:
        # Update_last_view_data in a vehicle and commit
        result.last_view_data = datetime.utcnow()
        db.commit()
        return result
    raise HTTPException(status_code=404, detail="Could not find vehicle id")


def get_recently_used_vehicles(db: Session) -> list[Vehicles]:
    """
    Gives 5 most recently viewed vehicles sorted by last_viewed_data (DESC)
    (viewed a car, or repairing it)

    :param db:
    :return: list of Vehicles
    """
    return db.query(Vehicles).order_by(desc(Vehicles.last_view_data)).limit(5).all()


def change_data_in_vehicle(db: Session, vehicle_id: int, data: VehicleEditData) -> bool:
    vehicle = db.query(Vehicles).filter(Vehicles.id == vehicle_id).first()
    if not vehicle: return False

    for key, value in data.dict(exclude_unset=True).items():
        setattr(vehicle, key, value)
    # Update_last_view_data in a vehicle and commit
    vehicle.last_view_data = datetime.utcnow()
    db.commit()

    return True


def db_delete_vehicle(db: Session, vehicle_id) -> bool:
    vehicle = db.query(Vehicles).filter(Vehicles.id == vehicle_id).delete(synchronize_session=False)
    db.commit()
    if vehicle: return True
    return False
