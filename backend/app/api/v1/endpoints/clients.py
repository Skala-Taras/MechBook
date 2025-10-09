from fastapi import APIRouter, Depends, HTTPException
from app.dependencies.jwt import get_current_mechanic_id_from_cookie
from app.schemas.client import ClientCreate, ClientUpdate, ClientExtendedInfo
from app.services.client_service import ClientService

router = APIRouter()

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
        # Sprawdź czy to błąd duplikatu (conflict) czy inny błąd walidacji
        if "already exists" in error_msg:
            raise HTTPException(status_code=409, detail=error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

@router.get("/{client_id}", response_model=ClientExtendedInfo)
def get_client(
    client_id: int,
    mechanic_id: int = Depends(get_current_mechanic_id_from_cookie),
    client_service: ClientService = Depends(ClientService)
):
    try:
        client = client_service.get_client_details(client_id)
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
        return client_service.update_client_details(client_id, client_data)
    except ValueError:
        raise HTTPException(status_code=404, detail="Client not found")

@router.delete("/{client_id}", status_code=204)
def delete_client(
    client_id: int,
    mechanic_id: int = Depends(get_current_mechanic_id_from_cookie),
    client_service: ClientService = Depends(ClientService)
):
    try:
        client_service.remove_client(client_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Client not found")
