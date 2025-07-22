from typing import Optional

from pydantic import BaseModel

from app.schemas.vehicle import VehicleBasicInfo


class RepairCreate(BaseModel):
    repair_description: str
    notes: Optional[str] = None
    vehicle_id: int

class RepairEditData(BaseModel):
    repair_description: Optional[str] = None
    notes: Optional[str] = None
    vehicle_id: Optional[int] = None

class RepairBasicInfo(BaseModel):
    repair_date: str#data
    repair_description: str

    class Config:
        from_attributes = True

class RepairExtendedInfo(BaseModel):
    repair_date: str  # data
    repair_description: str
    notes: str
    vehicle : VehicleBasicInfo

    class Config:
        from_attributes = True
