from typing import Optional

from pydantic import BaseModel, constr

from app.schemas.client import ClientCreate


class VehicleCreate(BaseModel):
    model: str
    marka: str
    vin: Optional[constr(max_length=17, min_length=17)] = None #17 length
