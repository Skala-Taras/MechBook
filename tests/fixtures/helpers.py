"""
Funkcje pomocnicze do testowania API.

Te funkcje pomagają w:
- Rejestracji i logowaniu użytkowników
- Tworzeniu danych testowych przez API
- Weryfikacji odpowiedzi
"""
from typing import Dict, Any, Optional
from fastapi.testclient import TestClient


class AuthHelper:
    """Helper do operacji związanych z autentykacją."""
    
    BASE_URL = "/api/v1/auth"
    
    @staticmethod
    def register_user(
        client: TestClient,
        email: str = "test@example.com",
        name: str = "Test User",
        password: str = "password123"
    ) -> Dict[str, Any]:
        """
        Rejestruje nowego użytkownika.
        
        Returns:
            Dict z kluczami: response, status_code, data (jeśli sukces)
        """
        payload = {
            "email": email,
            "name": name,
            "password": password
        }
        response = client.post(f"{AuthHelper.BASE_URL}/register", json=payload)
        
        result = {
            "response": response,
            "status_code": response.status_code,
            "payload": payload
        }
        
        if response.status_code == 200:
            result["data"] = response.json()
        
        return result
    
    @staticmethod
    def login_user(
        client: TestClient,
        email: str = "test@example.com",
        password: str = "password123"
    ) -> Dict[str, Any]:
        """
        Loguje użytkownika.
        
        Returns:
            Dict z kluczami: response, status_code, has_cookie
        """
        payload = {
            "email": email,
            "password": password
        }
        response = client.post(f"{AuthHelper.BASE_URL}/login", json=payload)
        
        return {
            "response": response,
            "status_code": response.status_code,
            "has_cookie": "access_token" in client.cookies,
            "payload": payload
        }
    
    @staticmethod
    def register_and_login(
        client: TestClient,
        email: str = "test@example.com",
        name: str = "Test User",
        password: str = "password123"
    ) -> Dict[str, Any]:
        """
        Rejestruje i od razu loguje użytkownika (typowy flow).
        
        Returns:
            Dict z danymi rejestracji i logowania
        """
        register_result = AuthHelper.register_user(client, email, name, password)
        if register_result["status_code"] != 200:
            return register_result
        
        login_result = AuthHelper.login_user(client, email, password)
        
        return {
            "register": register_result,
            "login": login_result,
            "user_data": register_result.get("data"),
            "is_authenticated": login_result["has_cookie"]
        }
    
    @staticmethod
    def logout_user(client: TestClient) -> Dict[str, Any]:
        """Wylogowuje użytkownika."""
        response = client.post(f"{AuthHelper.BASE_URL}/logout")
        return {
            "response": response,
            "status_code": response.status_code,
            "cookie_cleared": "access_token" not in client.cookies
        }
    
    @staticmethod
    def get_current_mechanic(client: TestClient) -> Dict[str, Any]:
        """Pobiera dane zalogowanego mechanika."""
        response = client.get(f"{AuthHelper.BASE_URL}/get_mechanics")
        
        result = {
            "response": response,
            "status_code": response.status_code
        }
        
        if response.status_code == 200:
            result["data"] = response.json()
        
        return result


def assert_error_response(response, expected_status: int, expected_detail: str):
    """
    Pomocnik do weryfikacji odpowiedzi błędów.
    
    Args:
        response: Response z TestClient
        expected_status: Oczekiwany kod statusu
        expected_detail: Oczekiwana treść błędu
    """
    assert response.status_code == expected_status, \
        f"Expected {expected_status}, got {response.status_code}. Body: {response.text}"
    
    body = response.json()
    assert "detail" in body, f"Response doesn't contain 'detail'. Body: {body}"
    assert body["detail"] == expected_detail, \
        f"Expected detail '{expected_detail}', got '{body['detail']}'"


def assert_success_response(response, expected_status: int = 200):
    """
    Pomocnik do weryfikacji sukcesu.
    
    Args:
        response: Response z TestClient
        expected_status: Oczekiwany kod statusu (domyślnie 200)
    
    Returns:
        Zdekodowany JSON z odpowiedzi
    """
    assert response.status_code == expected_status, \
        f"Expected {expected_status}, got {response.status_code}. Body: {response.text}"
    
    return response.json()

