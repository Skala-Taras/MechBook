from typing import Optional

from pydantic import BaseModel


class RepairCreate(BaseModel):
    repair_date: str
    repair_description: str
    notes: Optional[str] = None
    vehicle_id: int
