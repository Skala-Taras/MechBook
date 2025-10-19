"""
Authentication endpoints tests (/api/v1/auth).
Tests registration, login, authorization, password recovery, and logout.
"""
import pytest
from fastapi.testclient import TestClient

from tests.fixtures.helpers import AuthHelper, assert_error_response, assert_success_response
from tests.fixtures.factories import MechanicFactory


# ============================================================================
# TESTY REJESTRACJI
# ============================================================================

@pytest.mark.api
@pytest.mark.auth
@pytest.mark.integration
class TestRegister:
    """Tests for POST /api/v1/auth/register"""
    
    def test_register_success(self, client: TestClient):
        """Successfully register a new user with valid data"""
        user_data = MechanicFactory.build(email="newuser@example.com", name="New User")
        result = AuthHelper.register_user(client, **user_data)
        
        # Debug: wypisz szczegóły jeśli błąd
        if result["status_code"] != 200:
            print(f"\nDEBUG: Status {result['status_code']}")
            print(f"DEBUG: Response text: {result['response'].text}")
        
        assert result["status_code"] == 200, \
            f"Registration failed: {result['response'].text}"
        data = result["data"]
        assert data["email"] == user_data["email"]
        assert isinstance(data["id"], int)
    
    def test_register_duplicate_email(self, client: TestClient):
        """Reject registration with already registered email"""
        email = "duplicate@example.com"
        AuthHelper.register_user(client, email=email, name="User One")
        
        response = client.post(
            f"{AuthHelper.BASE_URL}/register",
            json={"email": email, "name": "User Two", "password": "pass123"}
        )
        
        assert_error_response(response, 400, "Email already registered")
    
    def test_register_invalid_email(self, client: TestClient):
        """Reject registration with invalid email format"""
        response = client.post(
            f"{AuthHelper.BASE_URL}/register",
            json={"email": "not-an-email", "name": "Test", "password": "pass123"}
        )
        assert response.status_code == 422
    
    def test_register_password_too_short(self, client: TestClient):
        """Reject password shorter than 5 characters"""
        response = client.post(
            f"{AuthHelper.BASE_URL}/register",
            json={"email": "test@example.com", "name": "Test", "password": "1234"}
        )
        assert response.status_code == 422
    
    def test_register_password_too_long(self, client: TestClient):
        """Reject password longer than 15 characters"""
        response = client.post(
            f"{AuthHelper.BASE_URL}/register",
            json={"email": "test@example.com", "name": "Test", "password": "a" * 16}
        )
        assert response.status_code == 422


# ============================================================================
# TESTY LOGOWANIA
# ============================================================================

@pytest.mark.api
@pytest.mark.auth
@pytest.mark.integration
class TestLogin:
    """Tests for POST /api/v1/auth/login"""
    
    def test_login_success(self, client: TestClient):
        """Successfully login with valid credentials"""
        email = "login@example.com"
        password = "password123"
        AuthHelper.register_user(client, email=email, password=password)
        
        result = AuthHelper.login_user(client, email=email, password=password)
        
        assert result["status_code"] == 200
        assert result["has_cookie"] is True
    
    def test_login_user_not_found(self, client: TestClient):
        """Reject login for non-existent email"""
        response = client.post(
            f"{AuthHelper.BASE_URL}/login",
            json={"email": "nonexistent@example.com", "password": "pass123"}
        )
        assert_error_response(response, 404, "Not found mechanic")
    
    def test_login_wrong_password(self, client: TestClient):
        """Reject login with incorrect password"""
        email = "user@example.com"
        AuthHelper.register_user(client, email=email, password="correct123")
        
        response = client.post(
            f"{AuthHelper.BASE_URL}/login",
            json={"email": email, "password": "wrong_password"}
        )
        assert_error_response(response, 400, "Hasło jest nieprawidłowe")
    
    


# ============================================================================
# TESTY AUTORYZACJI
# ============================================================================

@pytest.mark.api
@pytest.mark.auth
@pytest.mark.integration
class TestAuthorization:
    """Tests for authorization and protected endpoints"""
    
    def test_get_mechanics_requires_auth(self, client: TestClient):
        """Reject access without authentication"""
        response = client.get(f"{AuthHelper.BASE_URL}/get_mechanics")
        assert_error_response(response, 401, "Token missing")
    
    def test_get_mechanics_success_after_login(self, client: TestClient):
        """Access protected endpoint with valid token"""
        email = "mechanic@example.com"
        result = AuthHelper.register_and_login(client, email=email)
        user_id = result["user_data"]["id"]
        
        mechanic_result = AuthHelper.get_current_mechanic(client)
        
        assert mechanic_result["status_code"] == 200
        assert mechanic_result["data"]["id"] == user_id
        assert mechanic_result["data"]["email"] == email


# ============================================================================
# TESTY WYLOGOWANIA
# ============================================================================

@pytest.mark.api
@pytest.mark.auth
@pytest.mark.integration
class TestLogout:
    """Tests for POST /api/v1/auth/logout"""
    
    def test_logout_clears_cookie(self, client: TestClient):
        """Logout clears the access_token cookie"""
        AuthHelper.register_and_login(client, email="logout@example.com")
        assert "access_token" in client.cookies
        
        result = AuthHelper.logout_user(client)
        
        assert result["status_code"] == 200
        assert result["cookie_cleared"] is True
    
    def test_after_logout_cannot_access_protected_endpoints(self, client: TestClient):
        """Cannot access protected endpoints after logout"""
        AuthHelper.register_and_login(client, email="test@example.com")
        AuthHelper.logout_user(client)
        
        response = client.get(f"{AuthHelper.BASE_URL}/get_mechanics")
        assert response.status_code == 401


# ============================================================================
# TESTS FOR RECOVERY PASSWORD (3-STEP PROCESS)
# ============================================================================

@pytest.mark.api
@pytest.mark.auth
@pytest.mark.integration
class TestPasswordRecovery:
    """Tests for password recovery with 6-digit verification code"""
    
    def test_step1_recover_password_returns_generic_message(self, client: TestClient):
        """
        Step 1: Request verification code
        Returns generic message to prevent user enumeration
        """
        response = client.post(
            f"{AuthHelper.BASE_URL}/recover-password",
            json={"email": "any@example.com"}
        )
        
        data = assert_success_response(response, 200)
        assert "kod" in data["message"].lower() or "verification code" in data["message"].lower()
    
    def test_step1_recover_password_for_existing_user(self, client: TestClient):
        """
        Step 1: Request code for existing user
        Should send email with 6-digit code
        """
        email = "recover@example.com"
        AuthHelper.register_user(client, email=email, password="oldpass123")
        
        response = client.post(
            f"{AuthHelper.BASE_URL}/recover-password",
            json={"email": email}
        )
        
        data = assert_success_response(response, 200)
        # Should return success message (code sent via email)
        assert response.status_code == 200
    
    def test_step2_verify_code_invalid(self, client: TestClient):
        """
        Step 2: Verify code - invalid code
        Should return 400 error
        """
        response = client.post(
            f"{AuthHelper.BASE_URL}/verify-code",
            json={"email": "test@example.com", "code": "000000"}
        )
        
        assert response.status_code == 400
        assert "Invalid" in response.json()["detail"] or "kod" in response.json()["detail"].lower()
    
    def test_step2_verify_code_wrong_format(self, client: TestClient):
        """
        Step 2: Verify code - wrong format
        Code should be 6 digits
        """
        response = client.post(
            f"{AuthHelper.BASE_URL}/verify-code",
            json={"email": "test@example.com", "code": "12345"}  # Only 5 digits
        )
        
        # Should fail (either validation or not found)
        assert response.status_code in [400, 422]
    
    def test_step3_reset_password_without_verification(self, client: TestClient):
        """
        Step 3: Reset password without verifying code first
        Should return 400 error
        """
        response = client.post(
            f"{AuthHelper.BASE_URL}/reset-password",
            json={"reset_token": "invalid-token", "new_password": "newpass123"}
        )
        
        assert response.status_code == 400
    
    def test_complete_flow_simulation(self, client: TestClient):
        """
        Simulate complete 3-step password reset flow
        Note: Cannot test full flow without actual email/DB verification code
        """
        email = "fullflow@example.com"
        AuthHelper.register_user(client, email=email, password="oldpass123")
        
        # Step 1: Request code
        response1 = client.post(
            f"{AuthHelper.BASE_URL}/recover-password",
            json={"email": email}
        )
        assert response1.status_code == 200
        
        # Step 2: Would verify code here (requires actual code from DB)
        # Step 3: Would reset password here (requires reset_token from step 2)
        # These steps require access to DB to get actual verification code

