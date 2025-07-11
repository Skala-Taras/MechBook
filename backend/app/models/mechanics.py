from sqlalchemy import Column, Integer, String

from app.db.base import Base

class Mechanic(Base):
    __tablename__ = "Mechanic"
    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, index=True)
    email: str = Column(String, unique=True, index=True)
    hashed_password = Column(String)