from pydantic import BaseModel
from typing import Optional

class ElasticSearchEntry(BaseModel):
    id: int
    type: str  # 'client' or 'vehicle'
    # Client-specific fields
    name: Optional[str] = None
    phone: Optional[str] = None
    
    # Vehicle-specific fields
    vin: Optional[str] = None
    mark: Optional[str] = None
    model: Optional[str] = None
    
    class Config:
        from_attributes = True

class SearchResult(BaseModel):
    id: int
    type: str  # 'client' or 'vehicle'

    # For clients: "First Last"
    name: Optional[str] = None

    # For vehicles: "Mark Model"
    mark: Optional[str] = None
    model: Optional[str] = None
    
    class Config:
        from_attributes = True
