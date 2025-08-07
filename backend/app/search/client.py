from elasticsearch import Elasticsearch
from app.core.config import settings

# A single, reusable client instance
es_client = Elasticsearch(
    hosts=[settings.ELASTIC_HOST]
)
