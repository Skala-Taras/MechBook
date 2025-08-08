from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.core.security import EncryptedType

class Vehicles(Base):
    __tablename__="vehicles"
    id: int = Column(Integer, primary_key=True, index=True)
    mark: str = Column(String, index=True, nullable=False)
    model: str = Column(String, index=True, nullable=False)
    vin: str = Column(EncryptedType, nullable=True, unique=True)
    last_view_data = Column(DateTime)
    client_id: int = Column(Integer, ForeignKey("clients.id"), nullable=False)

    #Reletionship
    repairs = relationship("Repairs", back_populates="vehicle")
    client = relationship("Clients", back_populates="vehicles")