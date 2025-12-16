from fastapi import APIRouter, Depends, HTTPException
from app.dependencies.jwt import get_current_mechanic_id_from_cookie
from app.schemas.client import ClientCreate, ClientUpdate, ClientExtendedInfo
from app.services.client_service import ClientService
from app.schemas.vehicle import VehicleBasicInfoForClient
import logging
router = APIRouter()
logger = logging.getLogger(__name__)
@router.get("/", response_model=list[ClientExtendedInfo])
def list_clients(
    page: int = 1,
    size: int = 10,
    mechanic_id: int = Depends(get_current_mechanic_id_from_cookie),
    client_service: ClientService = Depends(ClientService)
):
    """
    Get all clients for the authenticated mechanic with pagination.
    
    - **page**: Page number (default: 1)
    - **size**: Number of clients per page (default: 10, max: 100)
    
    Returns clients ordered by newest first.
    """
    # Limit max size to prevent abuse
    if size > 100:
        size = 100
    if size < 1:
        size = 10
    if page < 1:
        page = 1
    
    return client_service.list_all_clients(page, size, mechanic_id)

@router.get("/count", response_model=dict)
def count_clients(
    mechanic_id: int = Depends(get_current_mechanic_id_from_cookie),
    client_service: ClientService = Depends(ClientService)
):
    """
    Get total count of clients for the authenticated mechanic.
    
    Returns: {"count": <number>}
    """
    count = client_service.count_all_clients(mechanic_id)
    return {"count": count}

@router.post("/", response_model=ClientExtendedInfo, status_code=201)
def create_client(
    client_data: ClientCreate,
    mechanic_id: int = Depends(get_current_mechanic_id_from_cookie),
    client_service: ClientService = Depends(ClientService)
):
    try:
        return client_service.create_new_client(client_data, mechanic_id)
    except ValueError as e:
        error_msg = str(e)
        if "already exists" in error_msg:
            raise HTTPException(status_code=409, detail=error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        logger.error(f"CRITICAL ERROR in create_client: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

@router.get("/{client_id}", response_model=ClientExtendedInfo)
def get_client(
    client_id: int,
    mechanic_id: int = Depends(get_current_mechanic_id_from_cookie),
    client_service: ClientService = Depends(ClientService)
):
    try:
        client = client_service.get_client_details(client_id, mechanic_id)
        return client
    except ValueError:
        raise HTTPException(status_code=404, detail="Client not found")

@router.put("/{client_id}", response_model=ClientExtendedInfo)
def update_client(
    client_id: int,
    client_data: ClientUpdate,
    mechanic_id: int = Depends(get_current_mechanic_id_from_cookie),
    client_service: ClientService = Depends(ClientService)
):
    try:
        return client_service.update_client_details(client_id, client_data, mechanic_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Client not found")

@router.delete("/{client_id}", status_code=204)
def delete_client(
    client_id: int,
    mechanic_id: int = Depends(get_current_mechanic_id_from_cookie),
    client_service: ClientService = Depends(ClientService)
):
    try:
        client_service.remove_client(client_id, mechanic_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Client not found")

@router.get("/{client_id}/vehicles" , response_model=list[VehicleBasicInfoForClient], status_code=200)
def get_client_vehicles(
    client_id: int,
    page: int = 1,
    size: int = 3,
    mechanic_id: int = Depends(get_current_mechanic_id_from_cookie),
    client_service: ClientService = Depends(ClientService)
):
    try:
        return client_service.get_client_vehicles(client_id, page, size, mechanic_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Client not found")