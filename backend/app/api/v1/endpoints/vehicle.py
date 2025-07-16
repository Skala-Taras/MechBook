from datetime import datetime
from pyexpat.errors import messages

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.crud.client import create_client
from app.crud.vehicle import create_vehicle, get_extended_vehicle_and_client_data, get_recently_used_vehicles
from app.dependencies.db import get_db
from app.dependencies.jwt import get_current_mechanic_id_from_cookie
from app.models.vehicles import Vehicles
from app.schemas.vehicle import VehicleCreate, VehicleExtendedInfo, VehicleBasicInfo

router = APIRouter()


@router.post("/add_vehicle", status_code=201)
def add_vehicle(
        data: VehicleCreate,
        mechanic_id: int = Depends(get_current_mechanic_id_from_cookie),
        db: Session = Depends(get_db)
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


@router.put("detail/{vehicle_id}/edit")
def edit_vehicle_data(vehicle_id: int,
               db: Session = Depends(get_db),
               mechanic_id: int = Depends(get_current_mechanic_id_from_cookie)
        ):
    pass




@router.get("/detail/{vehicle_id}", response_model=VehicleExtendedInfo)
def detail(vehicle_id: int,
               db: Session = Depends(get_db),
               mechanic_id: int = Depends(get_current_mechanic_id_from_cookie)
        ):
    return get_extended_vehicle_and_client_data(db, vehicle_id)


@router.get("/recently_used", response_model=list[VehicleBasicInfo])
def recently_used(
        mechanic_id: int = Depends(get_current_mechanic_id_from_cookie),
        db: Session = Depends(get_db)
        ):
    all_vehicles = get_recently_used_vehicles(db)
    return all_vehicles
