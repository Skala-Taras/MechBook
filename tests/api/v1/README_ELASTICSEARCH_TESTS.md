# Testy Elasticsearch

## ⚠️ Wymagania

Te testy wymagają **działającego Elasticsearch**. Inne testy mockują ES, ale te muszą działać z prawdziwym serwerem.

## 🚀 Uruchamianie

### 1. Uruchom Elasticsearch
```bash
# Za pomocą Docker Compose
docker-compose up -d es

# Sprawdź czy działa
curl http://localhost:9200
```

### 2. Uruchom testy
```bash
# Wszystkie testy ES
pytest tests/api/v1/test_elasticsearch_cleanup.py -v

# Tylko testy z markerem elasticsearch
pytest -m elasticsearch -v

# Konkretny test
pytest tests/api/v1/test_elasticsearch_cleanup.py::TestElasticsearchClientDeletion::test_delete_client_removes_from_elasticsearch -v
```

## 📋 Co testują?

### test_delete_client_removes_from_elasticsearch
1. Tworzy klienta
2. Sprawdza czy jest w ES (wyszukiwanie)
3. Usuwa klienta
4. Sprawdza czy zniknął z ES

### test_delete_client_removes_vehicles_from_elasticsearch
1. Tworzy klienta i pojazd
2. Sprawdza czy pojazd jest w ES
3. Usuwa klienta
4. Sprawdza czy pojazd też zniknął z ES (cascade)

### test_delete_vehicle_removes_from_elasticsearch
1. Tworzy pojazd
2. Sprawdza czy jest w ES
3. Usuwa pojazd
4. Sprawdza czy zniknął z ES

## 🔧 Konfiguracja

### conftest_es.py vs conftest.py

**conftest.py** (domyślny):
- Mockuje `search_engine_service`
- Szybkie testy bez ES
- Używany przez większość testów

**conftest_es.py** (dla testów ES):
- **NIE** mockuje ES
- Wymaga działającego ES
- Czyści indeks przed każdym testem
- Używany przez `test_elasticsearch_cleanup.py`

### Jak to działa?

W pliku testowym:
```python
# Import conftest_es fixtures explicitly
pytest_plugins = ['tests.conftest_es']
```

To powoduje, że pytest używa fixtures z `conftest_es.py` zamiast `conftest.py`.

## 🐛 Troubleshooting

### Problem: "Elasticsearch not available"
**Rozwiązanie:** Uruchom Elasticsearch
```bash
docker-compose up -d es
```

### Problem: Testy failują - zwraca 0 wyników
**Możliwe przyczyny:**
1. ES nie jest uruchomiony
2. Indeks nie jest odświeżany
3. Dane nie są indeksowane

**Sprawdź:**
```bash
# Czy ES działa?
curl http://localhost:9200

# Czy indeks istnieje?
curl http://localhost:9200/_cat/indices

# Czy są dane w indeksie?
curl http://localhost:9200/clients_and_vehicles/_count
```

### Problem: Testy używają zamockowanego ES
**Symptom:** `search_service` jest MagicMock  
**Rozwiązanie:** Sprawdź czy `pytest_plugins = ['tests.conftest_es']` jest na początku pliku testowego

## 📊 Timing

Testy używają `wait_for_elasticsearch()` (1.5s) aby poczekać na:
- Indeksację po utworzeniu
- Usunięcie po delete

Jest to konieczne bo ES ma domyślny refresh interval 1 sekundę.

## 🎯 Celem testów

Upewnić się, że:
- ✅ Usuwanie klienta usuwa go z ES
- ✅ Usuwanie klienta usuwa wszystkie jego pojazdy z ES (cascade)
- ✅ Usuwanie pojazdu usuwa go z ES
- ✅ Wyszukiwanie nie zwraca usuniętych danych
