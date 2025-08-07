from fastapi import APIRouter
from app.api.v1.endpoints import auth, vehicles, repairs, search

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["Vehicles"])
api_router.include_router(repairs.router, prefix="/repairs", tags=["Repairs"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
