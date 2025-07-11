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