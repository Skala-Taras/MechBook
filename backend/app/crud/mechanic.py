from fastapi.params import Depends
from sqlalchemy.dialects.postgresql.pg8000 import ServerSideCursor
from app.core.security import hash_password
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.models.user import User
from app.schemas.user import UserCreate


def create_user(db: Session, user: UserCreate):
    hashed_password = hash_password(user.password)
    db_user = User(email=user.email, name=user.name, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

