from typing import List
from fastapi import APIRouter, Query, Depends
from app.dependencies.jwt import get_current_mechanic_id_from_cookie

from app.services.search_engine_service import search_service
from app.schemas.search import SearchResult

router = APIRouter()

@router.get("/", response_model=List[SearchResult])
def perform_search(
    q: str = Query(..., description="The search query string."),
    mechanic_id: int = Depends(get_current_mechanic_id_from_cookie)
):
    """
    Performs a unified search across clients and vehicles.
    - Fuzzy matching is enabled for typo tolerance.
    - Searches across client names, phone numbers, vehicle makes, models, and VINs.
    - Results are filtered by mechanic_id for multi-tenancy.
    """
    results = search_service.search(q, mechanic_id)
    return results
