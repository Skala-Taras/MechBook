from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.repositories.interfaces.repair_repository_interface import IRepairRepository
from app.repositories.repair_repository import RepairRepository
from app.services.repair_services import RepairService


def get_repair_service(db: Session = Depends(get_db)) -> RepairService:
    return RepairService(RepairRepository(db))