from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.core.security import EncryptedType

class Clients(Base):
    __tablename__="clients"
    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, nullable=False, index=True)
    last_name: str = Column(String, nullable=False, index=True)
    phone: str = Column(String, index=True, nullable=True)
    pesel: str = Column(EncryptedType, nullable=True)
    mechanic_id = Column(Integer, ForeignKey("mechanics.id"), nullable=False)

    #Reletionship
    mechanic = relationship("Mechanics", back_populates="clients")
    vehicles = relationship("Vehicles", back_populates="client", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('phone', 'mechanic_id', name='uq_phone_mechanic'),
        UniqueConstraint('pesel', 'mechanic_id', name='uq_pesel_mechanic'),
    )