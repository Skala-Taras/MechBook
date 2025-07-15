from sqlalchemy.orm import Session

from app.models.clients import Clients
from app.schemas.client import ClientCreate

def create_client(db: Session, client_data: ClientCreate, mechanic_id: int) -> int:
    new_client = Clients(**client_data.dict(), mechanic_id=mechanic_id)
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return new_client.id
