from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.clients import Clients
from app.models.vehicles import Vehicles
from app.services.search_engine_service import SearchService
from app.search.client import es_client

def reindex_all_data():
    """
    Reads all clients and vehicles from PostgreSQL and indexes them in Elasticsearch.
    """
    db: Session = SessionLocal()
    
    print("Clearing existing search index...")
    if es_client.indices.exists(index=SearchService.INDEX_NAME):
        es_client.indices.delete(index=SearchService.INDEX_NAME)
    
    print("Creating new search index with mappings...")
    SearchService.create_index_if_not_exists()

    try:
        # Index all clients
        clients = db.query(Clients).all()
        print(f"Found {len(clients)} clients to index...")
        for client in clients:
            SearchService.index_client(client)
        print("Clients indexed successfully.")

        # Index all vehicles
        vehicles = db.query(Vehicles).all()
        print(f"Found {len(vehicles)} vehicles to index...")
        for vehicle in vehicles:
            SearchService.index_vehicle(vehicle)
        print("Vehicles indexed successfully.")

    finally:
        db.close()

if __name__ == "__main__":
    print("--- Starting Full Data Re-index into Elasticsearch ---")
    reindex_all_data()
    print("--- Re-index Complete ---")
