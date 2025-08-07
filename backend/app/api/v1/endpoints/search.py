from typing import List
from fastapi import APIRouter, Query

from app.services.search_engine_service import SearchService
from app.schemas.search import SearchResult

router = APIRouter()

@router.get("/", response_model=List[SearchResult])
def perform_search(
    q: str = Query(..., description="The search query string.")
):
    """
    Performs a unified search across clients and vehicles.
    - Fuzzy matching is enabled for typo tolerance.
    - Searches across client names, phone numbers, vehicle makes, models, and VINs.
    """
    results = SearchService.search(q)
    return results
