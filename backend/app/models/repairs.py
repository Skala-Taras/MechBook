from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.db.base import Base


class Repairs(Base):
    __tablename__="repairs"
    id = Column(Integer, primary_key=True, index=True)
    repair_date = Column(DateTime)
    repair_description = Column(String, index=True, nullable=False)
    notes = Column(String, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)

    #Reletionship
    vehicle = relationship("Vehicles", back_populates="repairs")