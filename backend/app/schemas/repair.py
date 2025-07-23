from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.vehicle import VehicleBasicInfo


class RepairCreate(BaseModel):
    name: str
    repair_description: Optional[str] = None
    price: Optional[float] = None
    repair_date: datetime
    vehicle_id: int

class RepairEditData(BaseModel):
    name: Optional[str] = None
    repair_description: Optional[str] = None
    price: Optional[float] = None
    repair_data: Optional[datetime] = None
    vehicle_id: Optional[int] = None

class RepairBasicInfo(BaseModel):
    name: str
    price: float
    repair_date: datetime

    class Config:
        from_attributes = True

class RepairExtendedInfo(BaseModel):
    name: str
    repair_description: str
    price: float
    repair_date: datetime
    vehicle : VehicleBasicInfo

    class Config:
        from_attributes = True
