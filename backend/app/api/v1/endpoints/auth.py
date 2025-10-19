from fastapi import APIRouter, HTTPException, Body
from fastapi.params import Depends
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

from app.dependencies.jwt import get_current_mechanic_id_from_cookie
from app.core.security import verify_password, create_access_jwt_token
from app.crud import mechanic as crud_mechanic
from app.crud.mechanic import get_mechanic_by_email
from app.dependencies.db import get_db
from app.schemas.mechanic import MechanicCreate, MechanicOut, MechanicLogin, ChangePasswordRequest
from app.services.password_service import PasswordService

router = APIRouter()

@router.post("/register", response_model=MechanicOut)
def register(mechanic: MechanicCreate, db: Session = Depends(get_db)):
    if crud_mechanic.get_mechanic_by_email(db, str(mechanic.email)):
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
        raise HTTPException(status_code=400, detail="Hasło jest nieprawidłowe")

    data = {
        "sub": str(db_mechanic.id),
        "role": "mechanic"
    }
    token = create_access_jwt_token(data)
    response = JSONResponse(content={"message": "Zalogowano pomyślnie"})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,  
        samesite="None",  
        max_age=60*60*24*7
    )
    return response

@router.get("/get_mechanics")
def get_mechanic(db: Session = Depends(get_db), mechanic_id: int = Depends(get_current_mechanic_id_from_cookie)):
    db_mechanic = crud_mechanic.get_mechanic_by_id(db, mechanic_id)
    print(db_mechanic)

    return MechanicOut.model_validate(db_mechanic)

@router.post("/recover-password")
async def recover_password(
    email: str = Body(..., embed=True),
    password_service: PasswordService = Depends(PasswordService)
):
    """
    Step 1: Request a password recovery code.
    Sends a 6-digit verification code to the user's email.
    """
    result = await password_service.recover_password(email)
    return result

@router.post("/verify-code")
def verify_code(
    email: str = Body(...),
    code: str = Body(...),
    password_service: PasswordService = Depends(PasswordService)
):
    """
    Step 2: Verify the 6-digit code sent to email.
    Returns a reset_token if successful, which can be used to reset password.
    """
    result = password_service.verify_code(email, code)
    return result

@router.post("/reset-password")
def reset_password(
    reset_token: str = Body(...),
    new_password: str = Body(...),
    password_service: PasswordService = Depends(PasswordService)
):
    """
    Step 3: Reset the password using the reset_token from verify-code.
    """
    result = password_service.reset_password(reset_token, new_password)
    return result


@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest = Body(...),
    password_service: PasswordService = Depends(PasswordService),
    mechanic_id: int = Depends(get_current_mechanic_id_from_cookie)
):
    """
    Change the password of the current mechanic.
    """
    result = password_service.change_password(data.current_password, data.new_password, mechanic_id)
    return result

@router.post("/logout")
def logout():
    """Clear auth cookie and log out."""
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie(key="access_token", path="/")
    return response