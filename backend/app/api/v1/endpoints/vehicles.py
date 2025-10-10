from fastapi import APIRouter, Depends, HTTPException
from app.dependencies.jwt import get_current_mechanic_id_from_cookie
from app.interfaces.vehicle_service import IVehicleService
from app.services.vehicle_service import VehicleService
from app.schemas.vehicle import VehicleCreate, VehicleExtendedInfo, VehicleBasicInfo, VehicleEditData
from . import repairs

router = APIRouter()
router.include_router(repairs.router, prefix="/{vehicle_id}/repairs", tags=["Repairs"])

@router.post("/", status_code=201)
def add_vehicle(
        data: VehicleCreate,
        mechanic_id: int = Depends(get_current_mechanic_id_from_cookie),
        service: IVehicleService = Depends(VehicleService)
        ):
    try:
        vehicle_id = service.register_new_vehicle(data, mechanic_id)
        return {"vehicle_id": vehicle_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{vehicle_id}", response_model=VehicleExtendedInfo, status_code=200)
def edit_vehicle_data(
        vehicle_id: int,
        data: VehicleEditData,
        mechanic_id: int = Depends(get_current_mechanic_id_from_cookie),
        service: IVehicleService = Depends(VehicleService)
        ):
    try:
        return service.update_vehicle_information(vehicle_id, data)
    except ValueError:
        raise HTTPException(status_code=404, detail="Vehicle not found")

@router.get("/recent", response_model=list[VehicleBasicInfo])
def recently_used(
        page: int = 1,
        size: int = 8,
        mechanic_id: int = Depends(get_current_mechanic_id_from_cookie),
        service: IVehicleService = Depends(VehicleService)
        ):
    return service.list_recently_viewed_vehicles(page, size)

@router.get("/{vehicle_id}", response_model=VehicleExtendedInfo)
def detail(
        vehicle_id: int,
        mechanic_id: int = Depends(get_current_mechanic_id_from_cookie),
        service: IVehicleService = Depends(VehicleService)
        ):
    try:
        return service.get_vehicle_details(vehicle_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Vehicle not found")

@router.delete("/{vehicle_id}", status_code=204)
def delete_vehicle(
        vehicle_id: int,
        mechanic_id: int = Depends(get_current_mechanic_id_from_cookie),
        service: IVehicleService = Depends(VehicleService)
        ):
    try:
        service.delete_vehicle(vehicle_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Vehicle not found")


