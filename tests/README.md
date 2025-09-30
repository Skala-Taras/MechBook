# 📚 Dokumentacja Testów MechBook

## Struktura Testów

```
tests/
├── conftest.py              # Główna konfiguracja pytest (fixture'y)
├── fixtures/                # Helpery i fabryki danych testowych
│   ├── __init__.py
│   ├── helpers.py          # Funkcje pomocnicze (AuthHelper, etc.)
│   └── factories.py        # Fabryki danych (MechanicFactory, etc.)
├── api/                     # Testy API endpoints
│   └── v1/
│       ├── test_auth.py    # Testy autentykacji
│       ├── test_clients.py
│       ├── test_repairs.py
│       ├── test_search.py
│       └── test_vehicles.py
├── unit/                    # Testy jednostkowe
│   ├── test_security.py    # Testy funkcji security
│   ├── test_jwt.py
│   └── test_mailer.py
├── integration/             # Testy integracyjne
│   ├── test_mechanics_crud.py
│   └── test_repairs_flow.py
└── data/                    # Dane testowe (fixtures, pliki)
```

## 🚀 Uruchamianie Testów

### Wszystkie testy
```bash
pytest
```

### Tylko testy API
```bash
pytest -m api
```

### Tylko testy jednostkowe (szybkie)
```bash
pytest -m unit
```

### Tylko testy auth
```bash
pytest -m auth
```

### Konkretny plik
```bash
pytest tests/api/v1/test_auth.py
```

### Konkretny test
```bash
pytest tests/api/v1/test_auth.py::TestLogin::test_login_success
```

### Z pokryciem kodu
```bash
pytest --cov=backend/app --cov-report=html
```

### Tryb verbose (szczegółowy output)
```bash
pytest -vv
```

### Zatrzymaj na pierwszym błędzie
```bash
pytest -x
```

### Pokaż print statements
```bash
pytest -s
```

## 📋 Markery Testów

Dostępne markery (zdefiniowane w `pytest.ini`):

- `@pytest.mark.unit` - Testy jednostkowe (szybkie, bez DB)
- `@pytest.mark.integration` - Testy integracyjne (z DB)
- `@pytest.mark.api` - Testy endpointów API
- `@pytest.mark.auth` - Testy związane z autentykacją
- `@pytest.mark.slow` - Wolne testy (Elasticsearch, etc.)

Przykład użycia:
```python
@pytest.mark.unit
@pytest.mark.auth
def test_password_hashing():
    # ...
```

## 🔧 Fixture'y

### Dostępne globalne fixture'y (z `conftest.py`)

#### `test_engine`
- **Scope:** session
- **Opis:** Silnik bazy danych SQLite
- **Użycie:** Automatyczne, nie musisz używać bezpośrednio

#### `db_session`
- **Scope:** function
- **Opis:** Transakcyjna sesja bazy danych (auto-rollback po teście)
- **Użycie:**
```python
def test_create_mechanic(db_session):
    mechanic = Mechanics(email="test@example.com", name="Test")
    db_session.add(mechanic)
    db_session.commit()
    # Po teście wszystko zostanie cofnięte
```

#### `app`
- **Scope:** function
- **Opis:** Instancja FastAPI z nadpisanymi zależnościami
- **Użycie:** Automatyczne przez `client`

#### `client`
- **Scope:** function
- **Opis:** TestClient do testowania API
- **Użycie:**
```python
def test_endpoint(client):
    response = client.get("/api/v1/some-endpoint")
    assert response.status_code == 200
```

## 🏭 Fabryki Danych

### MechanicFactory

```python
from tests.fixtures.factories import MechanicFactory

# Pojedynczy mechanik
mechanic_data = MechanicFactory.build()
# -> {"email": "mechanic1@example.com", "name": "Mechanic 1", "password": "password123"}

# Z custom danymi
mechanic_data = MechanicFactory.build(email="custom@example.com")

# Wielu mechaników
mechanics = MechanicFactory.build_batch(5)
```

### ClientFactory, VehicleFactory
- Podobne API jak MechanicFactory
- Zobacz `tests/fixtures/factories.py` dla szczegółów

## 🛠️ Helpery Testowe

### AuthHelper

```python
from tests.fixtures.helpers import AuthHelper

def test_example(client):
    # Rejestracja
    result = AuthHelper.register_user(client, email="test@example.com")
    
    # Logowanie
    result = AuthHelper.login_user(client, email="test@example.com")
    
    # Rejestracja + Logowanie w jednym
    result = AuthHelper.register_and_login(client, email="test@example.com")
    
    # Pobranie danych zalogowanego użytkownika
    result = AuthHelper.get_current_mechanic(client)
    
    # Wylogowanie
    result = AuthHelper.logout_user(client)
```

### Helpery asercji

```python
from tests.fixtures.helpers import assert_error_response, assert_success_response

# Sprawdź błąd
assert_error_response(response, expected_status=400, expected_detail="Error message")

# Sprawdź sukces i zwróć JSON
data = assert_success_response(response, expected_status=200)
```

## 📝 Dobre Praktyki

### 1. Struktura testu (Arrange-Act-Assert)

```python
def test_example(client):
    # ARRANGE - Przygotuj dane i stan
    user_data = MechanicFactory.build(email="test@example.com")
    
    # ACT - Wykonaj akcję
    result = AuthHelper.register_user(client, **user_data)
    
    # ASSERT - Sprawdź rezultat
    assert result["status_code"] == 200
    assert result["data"]["email"] == user_data["email"]
```

### 2. Używaj docstringów

```python
def test_login_success(client):
    """
    GIVEN: Zarejestrowany użytkownik
    WHEN: Logowanie z poprawnymi danymi
    THEN: Status 200, ustawione ciastko access_token
    """
    # ...
```

### 3. Grupuj testy w klasy

```python
@pytest.mark.api
@pytest.mark.auth
class TestLogin:
    """Testy logowania"""
    
    def test_login_success(self, client):
        # ...
    
    def test_login_wrong_password(self, client):
        # ...
```

### 4. Używaj parametryzacji dla wielu przypadków

```python
@pytest.mark.parametrize("email,expected_status", [
    ("valid@example.com", 200),
    ("invalid-email", 422),
    ("", 422),
])
def test_email_validation(client, email, expected_status):
    response = client.post("/register", json={"email": email, ...})
    assert response.status_code == expected_status
```

### 5. Izolacja testów

- Każdy test powinien być niezależny
- Nie polegaj na kolejności wykonywania testów
- Używaj fixture'ów do przygotowania stanu
- Baza danych jest automatycznie czyszczona (rollback)

### 6. Nazewnictwo

- `test_<funkcjonalność>_<scenariusz>`
- `test_login_success`
- `test_register_duplicate_email`
- `test_get_mechanics_requires_auth`

## 🐛 Debugowanie

### 1. Wyświetl szczegóły błędu

```bash
pytest -vv --tb=long
```

### 2. Zatrzymaj na błędzie i otwórz debugger

```bash
pytest --pdb
```

### 3. Uruchom tylko nieudane testy

```bash
pytest --lf  # last failed
```

### 4. Dodaj print do testu

```python
def test_example(client):
    response = client.post("/register", json={"email": "test@example.com"})
    print(f"Status: {response.status_code}")
    print(f"Body: {response.json()}")
    assert response.status_code == 200
```

Uruchom z `-s`:
```bash
pytest tests/api/v1/test_auth.py -s
```

## 🔄 Continuous Integration

W CI/CD pipeline możesz użyć:

```bash
# Szybkie testy (unit)
pytest -m unit

# Wszystkie testy z pokryciem
pytest --cov=backend/app --cov-report=xml --cov-report=term

# Tylko krytyczne testy
pytest -m "auth or api"
```

## 📊 Pokrycie Kodu

### Generuj raport HTML

```bash
pytest --cov=backend/app --cov-report=html
```

Otwórz `htmlcov/index.html` w przeglądarce.

### Minimalne pokrycie

```bash
pytest --cov=backend/app --cov-fail-under=80
```

## ❓ FAQ

**Q: Dlaczego testy nie widzą moich zmian w kodzie?**
A: Upewnij się, że nie masz uruchomionego serwera w tle. Zrestartuj pytest.

**Q: Jak testować z prawdziwym PostgreSQL?**
A: Zmień `TEST_DB_URL` w `conftest.py` na PostgreSQL i uruchom kontener przed testami.

**Q: Jak testować z prawdziwym Elasticsearch?**
A: Usuń monkeypatch dla `create_index_if_not_exists` i uruchom ES lokalnie. Oznacz testy jako `@pytest.mark.slow`.

**Q: Testy są wolne, jak je przyspieszyć?**
A: 
- Uruchamiaj równolegle: `pytest -n auto` (wymaga `pytest-xdist`)
- Uruchamiaj tylko zmienione: `pytest --testmon`
- Używaj SQLite zamiast Postgres dla większości testów

**Q: Jak testować wysyłanie maili?**
A: Używamy fake service (już zrobione w `conftest.py`). Dla prawdziwych maili użyj `pytest-mock` i mockuj `smtplib`.

## 📚 Dodatkowe Zasoby

- [Dokumentacja pytest](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)

---

**Autor:** MechBook Team  
**Ostatnia aktualizacja:** 2025-09-30

