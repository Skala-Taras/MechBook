from fastapi import FastAPI
from app.api.v1.api_router import api_router
from app.db.base import Base
from app.db.session import engine
from app.services.search_engine_service import SearchService

app = FastAPI()
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    SearchService.create_index_if_not_exists()
