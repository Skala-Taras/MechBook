from fastapi import APIRouter
from app.api.v1.endpoints import auth
from app.api.v1.endpoints import vehicles

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["Vehicles"])
