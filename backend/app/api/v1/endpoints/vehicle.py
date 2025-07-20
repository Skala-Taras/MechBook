from datetime import datetime
from pyexpat.errors import messages

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.crud.client import create_client
from app.crud.vehicle import create_vehicle, get_extended_vehicle_and_client_data, get_recently_used_vehicles, \
    change_data_in_vehicle, db_delete_vehicle
from app.dependencies.db import get_db
from app.dependencies.jwt import get_current_mechanic_id_from_cookie
from app.models.vehicles import Vehicles
from app.schemas.vehicle import VehicleCreate, VehicleExtendedInfo, VehicleBasicInfo, VehicleEditData

router = APIRouter()


@router.post("/vehicles/add_vehicle", status_code=201)
def add_vehicle(
        data: VehicleCreate,
        db: Session = Depends(get_db),
        mechanic_id: int = Depends(get_current_mechanic_id_from_cookie)
        ):
    if data.client_id:
        client_id = data.client_id
    elif data.client:
        client_id = create_client(db, data.client, mechanic_id)
    else:
        raise HTTPException(status_code=400, detail="Provide client_id or client_data")

    new_vehicle_data = {
        "mark": data.mark,
        "model": data.model,
        "vin": data.vin,
        "client_id": client_id,
        "last_view_data": datetime.utcnow(),
    }

    new_vehicle = create_vehicle(db, new_vehicle_data)

    return new_vehicle.id


@router.put("/vehicles/{vehicle_id}", status_code=200)
def edit_vehicle_data(
        vehicle_id: int,
        data: VehicleEditData,
        db: Session = Depends(get_db),
        mechanic_id: int = Depends(get_current_mechanic_id_from_cookie)
        ):
    updated = change_data_in_vehicle(db, vehicle_id, data)
    if updated:
        return {"message": "vehicle updated"}

    raise HTTPException(status_code=400, detail="Not found")


@router.get("/vehicles/recently", response_model=list[VehicleBasicInfo])
def recently_used(
        db: Session = Depends(get_db),
        mechanic_id: int = Depends(get_current_mechanic_id_from_cookie)
        ):
    print("Start")
    all_vehicles = get_recently_used_vehicles(db)
    print(all_vehicles)
    return all_vehicles



@router.get("/vehicles/{vehicle_id}", response_model=VehicleExtendedInfo)
def detail(
        vehicle_id: int,
        db: Session = Depends(get_db),
        mechanic_id: int = Depends(get_current_mechanic_id_from_cookie)
        ):
    return get_extended_vehicle_and_client_data(db, vehicle_id)


@router.delete("/vehicles/{vehicle_id}", status_code=202)
def delete_vehicle(
        vehicle_id: int,
        db: Session = Depends(get_db),
        mechanic_id: int = Depends(get_current_mechanic_id_from_cookie)
        ):
    result: bool = db_delete_vehicle(db, vehicle_id)
    if result:
        return {"message": "Vehicle was deleted"}
    raise HTTPException(status_code=404, detail="Could not find vehicle id")
