import sys
import os

# Add the backend directory to Python path for Docker compatibility
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy.orm import Session, joinedload
from app.db.session import SessionLocal
from app.models.clients import Clients
from app.models.vehicles import Vehicles
from app.services.search_engine_service import search_service
from app.search.client import es_client

def reindex_all_data():
    """
    Reads all clients and vehicles from PostgreSQL and indexes them in Elasticsearch.
    """
    db: Session = SessionLocal()
    
    print("Clearing existing search index...")
    if es_client.indices.exists(index=search_service.INDEX_NAME):
        es_client.indices.delete(index=search_service.INDEX_NAME)
    
    print("Creating new search index with mappings...")
    search_service.create_index_if_not_exists()

    try:
        # Index all clients
        clients = db.query(Clients).all()
        print(f"Found {len(clients)} clients to index...")
        for client in clients:
            search_service.index_client(client)
        print("Clients indexed successfully.")

        # Index all vehicles
        vehicles = db.query(Vehicles).options(joinedload(Vehicles.client)).all()
        print(f"Found {len(vehicles)} vehicles to index...")
        for vehicle in vehicles:
            search_service.index_vehicle(vehicle)
        print("Vehicles indexed successfully.")

    finally:
        db.close()

if __name__ == "__main__":
    print("--- Starting Full Data Re-index into Elasticsearch ---")
    reindex_all_data()
    print("--- Re-index Complete ---")
