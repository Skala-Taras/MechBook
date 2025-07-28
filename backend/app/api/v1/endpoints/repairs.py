from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from app.dependencies.jwt import get_current_mechanic_id_from_cookie
from app.schemas.repair import RepairCreate, RepairEditData, RepairExtendedInfo, RepairBasicInfo
from app.interfaces.repair_service import IRepairService
from app.services.repair_services import RepairService

router = APIRouter()

@router.post("/", status_code=201, response_model=RepairExtendedInfo)
def create_repair_for_vehicle(
        vehicle_id: int,
        repair_data: RepairCreate,
        mechanic_id: int = Depends(get_current_mechanic_id_from_cookie),
        service: IRepairService = Depends(RepairService)
        ):
    try:
        return service.log_new_repair_for_vehicle(vehicle_id, repair_data)
    except ValueError:
        raise HTTPException(status_code=404, detail="Repair not found")

@router.get("/", response_model=list[RepairBasicInfo])
def get_all_repairs_for_vehicle(
        vehicle_id: int,
        page: int = 1,
        size: int = 10,
        mechanic_id: int = Depends(get_current_mechanic_id_from_cookie),
        service: IRepairService = Depends(RepairService)
        ):
    return service.list_repairs_for_vehicle(
        vehicle_id=vehicle_id, page=page, size=size
    )

@router.patch("/{repair_id}", status_code=204)
def update_repair_details(
        repair_id: int,
        repair_data: RepairEditData,
        vehicle_id: int = Depends(lambda: 0), 
        mechanic_id: int = Depends(get_current_mechanic_id_from_cookie),
        service: IRepairService = Depends(RepairService)
        ):
    try:
        service.update_repair_information(repair_id, repair_data)
    except ValueError:
        raise HTTPException(status_code=404, detail="Repair not found")

@router.get("/{repair_id}", response_model=RepairExtendedInfo)
def get_repair_details(
        repair_id: int,
        vehicle_id: int = Depends(lambda: 0), # Placeholder
        mechanic_id: int = Depends(get_current_mechanic_id_from_cookie),
        service: IRepairService = Depends(RepairService)
        ):
    try:
        return service.get_repair_details(repair_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Repair not found")

@router.delete("/{repair_id}", status_code=204)
def delete_repair_by_id(
        repair_id: int,
        vehicle_id: int = Depends(lambda: 0), # Placeholder
        service: IRepairService = Depends(RepairService)
        ):
    try:
        service.delete_repair(repair_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Repair not found")
