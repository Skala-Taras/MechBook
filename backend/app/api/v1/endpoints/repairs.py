from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.jwt import get_current_mechanic_id_from_cookie
from app.dependencies.repair_service import get_repair_service
from app.schemas.repair import RepairCreate, RepairEditData, RepairExtendedInfo, RepairBasicInfo
from app.services.repair_services import RepairService

router = APIRouter()


@router.post("/", status_code=201)
def create_repair(
        repair_data: RepairCreate,
        mechanic_id: int = Depends(get_current_mechanic_id_from_cookie),
        service: RepairService = Depends(get_repair_service)
        ):
    return {"repair_id": service.create(repair_data)}

@router.get("/recently", response_model=list[RepairBasicInfo])
def get_recent_repairs(
        mechanic_id: int = Depends(get_current_mechanic_id_from_cookie),
        service: RepairService = Depends(get_repair_service)
        ):
    return service.recently()


@router.put("/{repair_id}", status_code=204)
def update_repair(
        repair_id: int,
        repair_data: RepairEditData,
        mechanic_id: int = Depends(get_current_mechanic_id_from_cookie),
        service: RepairService = Depends(get_repair_service)
        ):
    try:
        service.edit_data(repair_id, repair_data)
    except ValueError:
        raise HTTPException(status_code=404, detail="Repair not found")

@router.get("/{repair_id}", response_model=RepairExtendedInfo)
def get_repair(
        repair_id: int,
        mechanic_id: int = Depends(get_current_mechanic_id_from_cookie),
        service: RepairService = Depends(get_repair_service)
        ):
    try:
        return service.get(repair_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Repair not found")

@router.delete("/{repair_id}", status_code=204)
def delete_repair(
        repair_id: int,
        service: RepairService = Depends(get_repair_service)
        ):
    try:
        service.delete(repair_id)
        return {"message": "success"}
    except ValueError:
        raise HTTPException(status_code=404, detail="Repair not found")
