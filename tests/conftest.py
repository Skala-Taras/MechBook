"""
Główna konfiguracja testów PyTest.

Ten plik zawiera fixture'y, które są dostępne dla wszystkich testów:
- test_engine: silnik bazy danych SQLite (scope: session)
- db_session: sesja dla każdego testu z czyszczeniem bazy
- app: instancja FastAPI z nadpisanymi zależnościami
- client: TestClient do testowania API
"""
import os
import sys
import pathlib
import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

# ============================================================================
# KONFIGURACJA ŚRODOWISKA
# ============================================================================
os.environ.setdefault("URL_DB", "sqlite:///./.tmp_dummy.db")
os.environ.setdefault("ELASTIC_HOST", "http://localhost:9200")
os.environ.setdefault("jwt_secret_key", "test_secret_key_12345")
os.environ.setdefault("algorithm", "HS256")
os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
os.environ.setdefault("FRONTEND_URL", "http://localhost:3000")
os.environ.setdefault("MAIL_USERNAME", "test@example.com")
os.environ.setdefault("MAIL_PASSWORD", "password")
os.environ.setdefault("MAIL_FROM", "noreply@example.com")
os.environ.setdefault("MAIL_PORT", "587")
os.environ.setdefault("MAIL_SERVER", "smtp.example.com")
os.environ.setdefault("MAIL_STARTTLS", "true")
os.environ.setdefault("MAIL_SSL_TLS", "false")

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.chdir(str(BACKEND_DIR))

# Mockuj Elasticsearch PRZED importem aplikacji
sys.modules['app.services.search_engine_service'] = MagicMock()

# Teraz bezpiecznie importuj
from app.db.base import Base
from app.dependencies.db import get_db

TEST_DB_PATH = BACKEND_DIR / "test.db"
TEST_DB_URL = f"sqlite:///{TEST_DB_PATH}"

# ============================================================================
# FIXTURE'Y BAZY DANYCH
# ============================================================================

@pytest.fixture(scope="session")
def test_engine():
    """Tworzy silnik bazy danych raz na całą sesję testową."""
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    
    import time
    time.sleep(0.1)
    
    try:
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()
    except PermissionError:
        pass


@pytest.fixture(scope="function")
def db_session(test_engine) -> Session:
    """
    Sesja bazy danych dla każdego testu.
    
    Przed każdym testem czyści wszystkie tabele, aby testy były izolowane.
    """
    # Czyść wszystkie tabele przed testem
    connection = test_engine.connect()
    for table in reversed(Base.metadata.sorted_tables):
        connection.execute(table.delete())
    connection.commit()
    connection.close()
    
    # Utwórz nową sesję dla testu
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = SessionLocal()
    
    yield session
    
    session.close()


# ============================================================================
# FIXTURE'Y APLIKACJI
# ============================================================================

@pytest.fixture(scope="function")
def app(db_session: Session):
    """Zwraca instancję FastAPI z nadpisanymi zależnościami."""
    # Import app po mockowaniu Elasticsearch
    from app.main import app as fastapi_app
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    fastapi_app.dependency_overrides[get_db] = override_get_db
    
    # Fake password service
    class FakePasswordService:
        async def recover_password(self, email: str):
            return {"message": "If an account with that email exists, a password reset link has been sent."}
        
        def reset_password(self, token: str, new_password: str):
            return {"message": "Password has been reset successfully."}
    
    from app.services.password_service import PasswordService
    fastapi_app.dependency_overrides[PasswordService] = lambda: FakePasswordService()
    
    yield fastapi_app
    
    fastapi_app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(app):
    """Zwraca TestClient FastAPI do testowania endpointów HTTP."""
    with TestClient(app, raise_server_exceptions=True) as test_client:
        yield test_client


# ============================================================================
# FIXTURE'Y FABRYK
# ============================================================================

@pytest.fixture(autouse=True, scope="function")
def reset_factories():
    """Automatycznie resetuje wszystkie fabryki przed każdym testem."""
    from tests.fixtures.factories import reset_all_factories
    reset_all_factories()
