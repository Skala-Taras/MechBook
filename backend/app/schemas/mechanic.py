from pydantic import BaseModel, constr, EmailStr


class MechanicCreate(BaseModel):
    email: EmailStr
    name: str
    password: constr(
        min_length=5,
        max_length=15
    )

class MechanicLogin(BaseModel):
    email: EmailStr
    password: str

class MechanicOut(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    
class VerifyCodeRequest(BaseModel):
    email: EmailStr 
    code: constr(min_length=6, max_length=6, pattern=r'^\d+$')  

class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: constr(min_length=5, max_length=15)