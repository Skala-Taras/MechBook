from fastapi import APIRouter, HTTPException, Response
from fastapi.params import Depends
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

from app.dependencies.jwt import get_current_mechanic_id_from_cookie
from app.core.security import verify_password, create_access_jwt_token
from app.crud import mechanic as crud_mechanic
from app.crud.mechanic import get_mechanic_by_email
from app.dependencies.db import get_db
from app.schemas.mechanic import MechanicCreate, MechanicOut, MechanicLogin

router = APIRouter()

@router.post("/register", response_model=MechanicOut)
def register(mechanic: MechanicCreate, db: Session = Depends(get_db)):
    if crud_mechanic.get_mechanic_by_email(db, mechanic.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    created_mechanic = crud_mechanic.create_mechanic(db, mechanic)
    return MechanicOut.model_validate(created_mechanic)

@router.post("/login")
def login(mechanic: MechanicLogin, db: Session = Depends(get_db)):
    db_mechanic = get_mechanic_by_email(db, mechanic.email)
    print(mechanic.email, db_mechanic)
    if not db_mechanic:
        raise HTTPException(status_code=404, detail="Not found mechanic")
    if not verify_password(mechanic.password, db_mechanic.hashed_password):
        raise HTTPException(status_code=400, detail="Password is incorrect")

    data = {
        "sub": str(db_mechanic.id),
        "role": "mechanic"
    }
    token = create_access_jwt_token(data)
    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=60
    )
    return response

@router.get("/get_mechanics")
def get_mechanic(db: Session = Depends(get_db), mechanic_id: int = Depends(get_current_mechanic_id_from_cookie)):
    db_mechanic = crud_mechanic.get_mechanic_by_id(db, mechanic_id)
    print(db_mechanic)

    return MechanicOut.model_validate(db_mechanic)