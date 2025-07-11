from fastapi import APIRouter
from app.schemas.user import UserCreate, UserOut
router = APIRouter()

@router.post("/register", response_model=UserOut)

