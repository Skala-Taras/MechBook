from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base

class Clients(Base):
    __tablename__="clients"
    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, nullable=False, index=True)
    last_name: str = Column(String, nullable=False, index=True)
    phone: str = Column(String, index=True, nullable=True, unique=True)
    pesel: str = Column(String(length=11), index=True, nullable=True, unique=True)
    mechanic_id = Column(Integer, ForeignKey="mechanics.id", nullable=False)

    #Reletionship
    mechanic = relationship("Mechanics", back_populates="clients")
    vehicles = relationship("Vehicles", back_populates="client")