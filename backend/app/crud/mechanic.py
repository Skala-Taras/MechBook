from app.core.security import hash_password
from sqlalchemy.orm import Session
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

def get_mechanic_by_id(db: Session, mechanic_id: int):
    return db.query(Mechanics).filter(Mechanics.id == mechanic_id).first()

def update_mechanic_password(db: Session, mechanic: Mechanics, new_password_hash: str):
    mechanic.hashed_password = new_password_hash
    db.commit()
    db.refresh(mechanic)
