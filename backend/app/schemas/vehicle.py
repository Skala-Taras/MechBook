from typing import Optional

from pydantic import BaseModel, constr

from app.schemas.client import ClientCreate, ClientBasicInfo, ClientExtendedInfo


class VehicleCreate(BaseModel):
    model: str
    mark: str
    vin: Optional[constr(max_length=17, min_length=17)] = None #17 length
    client_id: Optional[int] = None
    client: Optional[ClientCreate] = None

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
    client: ClientExtendedInfo

    class Config:
        from_attributes = True