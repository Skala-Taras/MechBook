from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base

class Mechanics(Base):
    __tablename__ = "Mechanic"
    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, nullable=False, index=True)
    email: str = Column(String, nullable=False, unique=True, index=True)
    hashed_password = Column(String, nullable=False,)

    #Reletionship
    clients = relationship("Clients", back_populates="mechanic")