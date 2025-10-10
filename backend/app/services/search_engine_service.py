from app.search.client import es_client
from app.models.clients import Clients
from app.models.vehicles import Vehicles
from app.schemas.search import ElasticSearchEntry, SearchResult

class SearchService:
    INDEX_NAME = "clients_and_vehicles"

    def create_index_if_not_exists(self):
        """
        Creates the search index with advanced mappings if it doesn't exist.
        """
        if not es_client.indices.exists(index=self.INDEX_NAME):
            settings = {
                "analysis": {
                    "char_filter": {
                        "whitespace_remove_filter": {
                            "type": "pattern_replace",
                            "pattern": "\\s+",
                            "replacement": ""
                        }
                    },
                    "analyzer": {
                        "autocomplete_analyzer": {
                            "tokenizer": "autocomplete_tokenizer",
                            "filter": ["lowercase"]
                        },
                        "whitespace_remove_analyzer": {
                            "tokenizer": "standard",
                            "filter": ["lowercase"],
                            "char_filter": ["whitespace_remove_filter"]
                        }
                    },
                    "tokenizer": {
                        "autocomplete_tokenizer": {
                            "type": "edge_ngram",
                            "min_gram": 2,
                            "max_gram": 20,
                            "token_chars": ["letter", "digit"]
                        }
                    }
                }
            }
            mappings = {
                "properties": {
                    "type": {"type": "keyword"},
                    "mechanic_id": {"type": "integer"},
                    "name": {
                        "type": "text",
                        "fields": {
                            "autocomplete": {
                                "type": "text",
                                "analyzer": "autocomplete_analyzer",
                                "search_analyzer": "standard"
                            },
                            "no_whitespace": {
                                "type": "text",
                                "analyzer": "whitespace_remove_analyzer"
                            }
                        }
                    },
                    "phone": {"type": "keyword"},
                    "vin": {"type": "keyword"},
                    "client_id": {"type": "integer"},
                    "client_name": {
                        "type": "text",
                        "fields": {
                            "autocomplete": {
                                "type": "text",
                                "analyzer": "autocomplete_analyzer",
                                "search_analyzer": "standard"
                            }
                        }
                    },
                    "client_last_name": {
                        "type": "text",
                        "fields": {
                            "autocomplete": {
                                "type": "text",
                                "analyzer": "autocomplete_analyzer",
                                "search_analyzer": "standard"
                            }
                        }
                    }
                }
            }
            es_client.indices.create(
                index=self.INDEX_NAME,
                body={"settings": settings, "mappings": mappings}
            )

    def index_client(self, client: Clients):
        doc = ElasticSearchEntry(
            id=client.id,
            type="client",
            mechanic_id=client.mechanic_id,
            name=f"{client.name} {client.last_name}",
            phone=client.phone,
        )
        es_client.index(
            index=self.INDEX_NAME,
            id=f"client-{client.id}",
            document=doc.dict(exclude_none=True)
        )


    def index_vehicle(self, vehicle: Vehicles):
        if not vehicle.client:
            raise ValueError("Vehicle must have a client to be indexed.")
            
        doc = ElasticSearchEntry(
            id=vehicle.id,
            type="vehicle",
            mechanic_id=vehicle.client.mechanic_id,
            name=f"{vehicle.mark} {vehicle.model}",
            vin=vehicle.vin,
            client_id=vehicle.client_id,
            client_name=vehicle.client.name,
            client_last_name=vehicle.client.last_name
        )
        es_client.index(
            index=self.INDEX_NAME,
            id=f"vehicle-{vehicle.id}",
            document=doc.dict(exclude_none=True)
        )

    def delete_document(self, doc_id: str):
        es_client.delete(index=self.INDEX_NAME, id=doc_id, ignore=[404])

    def search(self, query: str, mechanic_id: int) -> list[SearchResult]:
        if not query:
            return []

        search_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "function_score": {
                                "query": {
                                    "multi_match": {
                                        "query": query,
                                        "fields": [
                                            "name^2",
                                            "name.autocomplete^1.5",
                                            "name.no_whitespace",
                                            "phone",
                                            "vin",
                                            "client_name^1.8",
                                            "client_name.autocomplete^1.5",
                                            "client_last_name^1.8",
                                            "client_last_name.autocomplete^1.5"
                                        ],
                                        "fuzziness": "AUTO",
                                        "type": "best_fields",
                                        "operator": "and"
                                    }
                                },
                                "functions": [
                                    {
                                        "filter": { "term": { "type": "client" } },
                                        "weight": 2
                                    }
                                ],
                                "boost_mode": "multiply"
                            }
                        }
                    ],
                    "filter": [
                        {
                            "term": { "mechanic_id": mechanic_id }
                        }
                    ]
                }
            }
        }

        response = es_client.search(index=self.INDEX_NAME, body=search_body)
        
        results = [
            SearchResult(**hit["_source"])
            for hit in response["hits"]["hits"]
        ]
        return results

search_service = SearchService()
