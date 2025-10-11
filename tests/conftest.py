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
# CONFIGURATION OF THE ENVIRONMENT
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

sys.modules['app.services.search_engine_service'] = MagicMock()

from app.db.base import Base
import app.models  # noqa: F401
from app.dependencies.db import get_db

TEST_DB_PATH = BACKEND_DIR / "test.db"
TEST_DB_URL = f"sqlite:///{TEST_DB_PATH}"

# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def test_engine():
    """Creates a database engine once for the entire test session."""
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
    Database session for each test.
    """
    # Clear all tables before each test
    connection = test_engine.connect()
    for table in reversed(Base.metadata.sorted_tables):
        connection.execute(table.delete())
    connection.commit()
    connection.close()
    
    # Create a new session for the test
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = SessionLocal()
    
    yield session
    
    session.close()


# ============================================================================
# APPLICATION FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
def app(db_session: Session):
    """Returns a FastAPI instance with overridden dependencies."""
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
            return {"message": "Jeśli istnieje konto z tym email, kod do resetu hasła został wysłany"}
        
        def verify_code(self, email: str, code: str):
            # Mock verification - validates code format and content
            from fastapi import HTTPException
            # Validate code length 
            if len(code) != 6 or not code.isdigit():
                raise HTTPException(status_code=400, detail="Invalid verification code format")
            # Invalid code for testing
            if code == "000000":
                raise HTTPException(status_code=400, detail="Invalid verification code")
            return {
                "message": "Kod został zweryfikowany",
                "reset_token": "fake-reset-token-for-testing"
            }
        
        def reset_password(self, reset_token: str, new_password: str):
            # Mock reset - fails if no token
            from fastapi import HTTPException
            if not reset_token or reset_token == "invalid-token":
                raise HTTPException(status_code=400, detail="Invalid or expired reset token")
            return {"message": "Password successfully reset"}
    
    from app.services.password_service import PasswordService
    fastapi_app.dependency_overrides[PasswordService] = lambda: FakePasswordService()
    
    yield fastapi_app
    
    fastapi_app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(app):
    """Returns a TestClient FastAPI for testing HTTP endpoints."""
    with TestClient(app, raise_server_exceptions=True) as test_client:
        yield test_client


# ============================================================================
# FACTORY FIXTURES
# ============================================================================

@pytest.fixture(autouse=True, scope="function")
def reset_factories():
    """Automatically resets all factories before each test."""
    from tests.fixtures.factories import reset_all_factories
    reset_all_factories()
