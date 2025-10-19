from typing import Optional

from pydantic import BaseModel, constr

from app.schemas.client import ClientCreate, ClientBasicInfo, ClientExtendedInfo


class VehicleCreate(BaseModel):
    model: str
    mark: str
    vin: Optional[constr(max_length=17, min_length=17)] = None #17 length
    client_id: Optional[int] = None
    client: Optional[ClientCreate] = None
    fuel_type: Optional[str] = None
    engine_capacity: Optional[float] = None
    engine_power: Optional[int] = None
    registration_number: Optional[str] = None

class VehicleBasicInfoForClient(BaseModel):
    id: int
    model: str
    mark: str

    class Config:
        from_attributes = True

class VehicleBasicInfo(BaseModel):
    id: int
    model: str
    mark: str
    client: ClientBasicInfo

    class Config:
        from_attributes = True

class VehicleExtendedInfo(BaseModel):
    id: int
    model: str
    mark: str
    vin: Optional[constr(max_length=17, min_length=17)] = None #17 length
    fuel_type: Optional[str] = None
    engine_capacity: Optional[float] = None
    engine_power: Optional[int] = None
    registration_number: Optional[str] = None
    client: ClientExtendedInfo

    class Config:
        from_attributes = True


class VehicleEditData(BaseModel):
    model: Optional[str] = None
    mark: Optional[str] = None
    vin: Optional[constr(max_length=17, min_length=17)] = None
    client_id: Optional[int] = None
    fuel_type: Optional[str] = None
    engine_capacity: Optional[float] = None
    engine_power: Optional[int] = None
    registration_number: Optional[str] = None