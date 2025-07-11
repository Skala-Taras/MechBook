from fastapi import FastAPI
from app.api.v1.api_router import api_router
from app.db.base import Base
from app.db.session import engine

app = FastAPI()
app.include_router(api_router, prefix="/api/v1")

Base.metadata.create_all(bind=engine)
