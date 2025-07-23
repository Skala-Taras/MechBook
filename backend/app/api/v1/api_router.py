from fastapi import APIRouter
from app.api.v1.endpoints import auth
from app.api.v1.endpoints import vehicles
from app.api.v1.endpoints import repairs

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(vehicles.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(repairs.router, prefix="/repairs", tags=["Repairs"])
