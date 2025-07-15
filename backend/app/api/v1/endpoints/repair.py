from fastapi import FastAPI, APIRouter

router = APIRouter()

@router.add_repair()
def add_repair():
    pass