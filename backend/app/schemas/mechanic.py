from pydantic import BaseModel, constr, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: constr(
        min_length=5,
        max_length=15
    )

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True