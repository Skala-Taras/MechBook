from fastapi.params import Depends
from sqlalchemy.dialects.postgresql.pg8000 import ServerSideCursor
from app.core.security import hash_password
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.models.mechanics import Mechanics
from app.schemas.mechanic import MechanicCreate


def create_mechanic(db: Session, mechanic: MechanicCreate):
    hashed_password = hash_password(mechanic.password)
    db_mechanic = Mechanics(email=mechanic.email, name=mechanic.name, hashed_password=hashed_password)
    db.add(db_mechanic)
    db.commit()
    db.refresh(db_mechanic)
    return db_mechanic

def get_mechanic_by_email(db: Session, email: str):
    return db.query(Mechanics).filter(Mechanics.email == email).first()

def get_mechanic_by_id(db: Session, id_mechanic: int):
    return db.query(Mechanics).filter(Mechanics.id == id_mechanic).first()
