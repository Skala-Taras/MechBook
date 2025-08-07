from typing import Optional

from pydantic import BaseModel, constr


class ClientCreate(BaseModel):
    name: str
    last_name: str
    phone: Optional[str] = None
    pesel: Optional[constr(max_length=11, min_length=11)] = None


class ClientBasicInfo(BaseModel):
    id: int
    name: str
    last_name: str

    class Config:
        from_attributes = True

class ClientExtendedInfo(BaseModel):
    id: int
    name: str
    last_name: str
    phone: Optional[str] = None
    pesel: Optional[str] = None

    class Config:
        from_attributes = True

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    pesel: Optional[constr(max_length=11, min_length=11)] = None
