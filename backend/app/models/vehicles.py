from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint, Float
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.core.security import EncryptedType

class Vehicles(Base):
    __tablename__="vehicles"
    id: int = Column(Integer, primary_key=True, index=True)
    mark: str = Column(String, index=True, nullable=False)
    model: str = Column(String, index=True, nullable=False)
    vin: str = Column(EncryptedType, nullable=True)
    vin_hash: str = Column(String(64), index=True, nullable=True)
    fuel_type: str = Column(String(20), nullable=True)
    engine_capacity: float = Column(Float, nullable=True)
    engine_power: int = Column(Integer, nullable=True)
    registration_number: str = Column(String(32), index=True, nullable=True)
    last_view_data = Column(DateTime)
    client_id: int = Column(Integer, ForeignKey("clients.id"), nullable=False)
    mechanic_id: int = Column(Integer, ForeignKey("mechanics.id"), nullable=False)  

    #Reletionship
    repairs = relationship("Repairs", back_populates="vehicle", cascade="all, delete-orphan")
    client = relationship("Clients", back_populates="vehicles")
    
    # Composite unique constraint - VIN is unique per mechanic
    __table_args__ = (
        UniqueConstraint('vin_hash', 'mechanic_id', name='uq_vin_mechanic'),
    )