from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api_router import api_router
from app.db.base import Base
from app.db.session import engine
from app.services.search_engine_service import search_service

import app.models  # noqa

app = FastAPI()
app.include_router(api_router, prefix="/api/v1")

allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    f"https://'mech-book.com'.replace('https://', '').replace('http://', '')",
    f"https://www.'mech-book.com'.replace('https://', '').replace('http://', '')",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    search_service.create_index_if_not_exists()