from typing import List, Optional
from fastapi import Depends
from sqlalchemy.orm import Session

from app.interfaces.vehicle_service import IVehicleService
from app.interfaces.vehicle_repository import IVehicleRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.dependencies.db import get_db
from app.models.vehicles import Vehicles
from app.schemas.vehicle import VehicleCreate, VehicleEditData, VehicleExtendedInfo, VehicleBasicInfo
from datetime import datetime

from app.services.client_service import ClientService
from app.services.search_engine_service import search_service


class VehicleService(IVehicleService):
    
    def __init__(self, 
                 vehicle_repo: IVehicleRepository = Depends(VehicleRepository),
                 client_service: ClientService = Depends(ClientService),
                 db: Session = Depends(get_db)):
        self.vehicle_repo = vehicle_repo
        self.client_service = client_service
        self.db = db

    @staticmethod
    def __validate_correct_result(vehicle: Vehicles | bool | None) -> None:
        # Check if vehicle_id which was given is valid, if not raise ValueError
        if not vehicle:
            raise ValueError("Vehicle not found")

    def register_new_vehicle(self, data: VehicleCreate, mechanic_id: int) -> int:
        if data.client_id:
            # Verify the client belongs to this mechanic
            client = self.client_service.get_client_details(data.client_id, mechanic_id)
            if not client:
                raise ValueError("Client not found or does not belong to this mechanic")
            client_id = data.client_id
        elif data.client:
            new_client = self.client_service.create_new_client(data.client, mechanic_id)
            client_id = new_client.id
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
        search_service.index_vehicle(new_vehicle)
        return new_vehicle.id

    def get_vehicle_details(self, vehicle_id: int, mechanic_id: int) -> VehicleExtendedInfo:
        vehicle = self.vehicle_repo.get_vehicle_by_id(vehicle_id, mechanic_id)
        self.__validate_correct_result(vehicle)
        
        print(f"SERVICE LAYER: Fetched vehicle {vehicle.id}. VIN is '{vehicle.vin}' (decrypted).")

        self.vehicle_repo.update_last_view_column_in_vehicles(vehicle)
        return VehicleExtendedInfo.model_validate(vehicle)

    def list_recently_viewed_vehicles(self, page: int, size: int, mechanic_id: int) -> Optional[List[VehicleBasicInfo]]:
        vehicles = self.vehicle_repo.get_recently_viewed_vehicles(limit=size, page=page, mechanic_id=mechanic_id)
        return [VehicleBasicInfo.model_validate(vehicle) for vehicle in vehicles]

    def update_vehicle_information(self, vehicle_id: int, data: VehicleEditData, mechanic_id: int) -> VehicleExtendedInfo:
        updated_vehicle = self.vehicle_repo.update_vehicle(vehicle_id, data.dict(exclude_unset=True), mechanic_id)
        self.__validate_correct_result(updated_vehicle)
        
        search_service.index_vehicle(updated_vehicle)
        self.vehicle_repo.update_last_view_column_in_vehicles(updated_vehicle)
        return VehicleExtendedInfo.model_validate(updated_vehicle)

    def delete_vehicle(self, vehicle_id: int, mechanic_id: int) -> None:
        was_deleted = self.vehicle_repo.delete_vehicle(vehicle_id, mechanic_id)
        self.__validate_correct_result(was_deleted)
        search_service.delete_document(f"vehicle-{vehicle_id}")