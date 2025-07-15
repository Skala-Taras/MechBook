from typing import Optional

from pydantic import BaseModel, constr


class ClientCreate(BaseModel):
    name: str
    last_name: str
    phone: Optional[str] = None
    pesel: Optional[constr(max_length=11, min_length=11)] = None