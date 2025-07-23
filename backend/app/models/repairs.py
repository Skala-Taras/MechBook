from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship

from app.db.base import Base


class Repairs(Base):
    __tablename__="repairs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    repair_description = Column(String, index=True, nullable=True)
    price = Column(Float, index=True, nullable=True)
    repair_date = Column(DateTime, nullable=False)
    last_seen = Column(DateTime)        # To sort by an earlier date
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)

    #Reletionship
    vehicle = relationship("Vehicles", back_populates="repairs")