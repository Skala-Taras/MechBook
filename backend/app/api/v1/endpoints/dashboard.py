from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.dependencies.jwt import get_current_mechanic_id_from_cookie

router = APIRouter()

@router.post("/add_vehicle")
def add_vehicle(
        data,
        mechanic_id: int = Depends(get_current_mechanic_id_from_cookie),
        db: Session = Depends(get_db)
    ):
