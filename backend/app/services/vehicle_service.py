from typing import List, Optional
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.interfaces.vehicle_service import IVehicleService
from app.interfaces.vehicle_repository import IVehicleRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.dependencies.db import get_db
from app.models.vehicles import Vehicles
from app.crud.client import create_client
from app.schemas.vehicle import VehicleCreate, VehicleEditData, VehicleExtendedInfo, VehicleBasicInfo
from datetime import datetime

class VehicleService(IVehicleService):
    
    def __init__(self, vehicle_repo: IVehicleRepository = Depends(VehicleRepository), db: Session = Depends(get_db)):
        self.vehicle_repo = vehicle_repo
        self.db = db

    @staticmethod
    def __validate_correct_result(vehicle: Vehicles | bool | None) -> None:
        # Check if vehicle_id which was given is valid, if not raise ValueError
        if not vehicle:
            raise ValueError("Vehicle not found")

    def register_new_vehicle(self, data: VehicleCreate, mechanic_id: int) -> int:
        if data.client_id:
            client_id = data.client_id
        elif data.client:
            client_id = create_client(self.db, data.client, mechanic_id)
        else:
            raise ValueError("Client data or client_id must be provided.")

        new_vehicle_data = {
            "mark": data.mark,
            "model": data.model,
            "vin": data.vin,
            "client_id": client_id,
            "last_view_data": datetime.utcnow(),
        }
        
        new_vehicle = self.vehicle_repo.create_vehicle(new_vehicle_data)
        return new_vehicle.id

    def get_vehicle_details(self, vehicle_id: int) -> VehicleExtendedInfo:
        vehicle = self.vehicle_repo.get_vehicle_by_id(vehicle_id)
        self.__validate_correct_result(vehicle)
        self.vehicle_repo.update_last_view_column_in_vehicles(vehicle)
        return VehicleExtendedInfo.model_validate(vehicle)

    def list_recently_viewed_vehicles(self) -> Optional[List[VehicleBasicInfo]]:
        vehicles = self.vehicle_repo.get_recently_viewed_vehicles(limit=5)
        return [VehicleBasicInfo.model_validate(vehicle) for vehicle in vehicles]

    def update_vehicle_information(self, vehicle_id: int, data: VehicleEditData) -> VehicleExtendedInfo:
        updated_vehicle = self.vehicle_repo.update_vehicle(vehicle_id, data.dict(exclude_unset=True))
        self.__validate_correct_result(updated_vehicle)
        self.vehicle_repo.update_last_view_column_in_vehicles(updated_vehicle)
        return VehicleExtendedInfo.model_validate(updated_vehicle)

    def delete_vehicle(self, vehicle_id: int) -> None:
        was_deleted = self.vehicle_repo.delete_vehicle(vehicle_id)
        self.__validate_correct_result(was_deleted)