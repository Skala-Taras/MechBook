from typing import Dict, Any, Optional
from fastapi.testclient import TestClient


class AuthHelper:
    """Helper for operations related to authentication."""
    
    BASE_URL = "/api/v1/auth"
    
    @staticmethod
    def register_user(
        client: TestClient,
        email: str = "test@example.com",
        name: str = "Test User",
        password: str = "password123"
    ) -> Dict[str, Any]:
        """
        Registers a new user.
        
        Returns:
            Dict with keys: response, status_code, data (if success)
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
        Logs in a user.
        
        Returns:
            Dict with keys: response, status_code, has_cookie
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
    def login(
        client: TestClient,
        email: str = "test@example.com",
        password: str = "password123"
    ) -> Dict[str, Any]:
        """Alias for login_user for backward compatibility"""
        return AuthHelper.login_user(client, email, password)
    
    @staticmethod
    def register_and_login(
        client: TestClient,
        email: str = "test@example.com",
        name: str = "Test User",
        password: str = "password123"
    ) -> Dict[str, Any]:
        """
        Registers and immediately logs in a user (typical flow).
        
        Returns:
            Dict with registration and login data
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
        """Logs out a user."""
        response = client.post(f"{AuthHelper.BASE_URL}/logout")
        return {
            "response": response,
            "status_code": response.status_code,
            "cookie_cleared": "access_token" not in client.cookies
        }
    
    @staticmethod
    def get_current_mechanic(client: TestClient) -> Dict[str, Any]:
        """Gets data of the logged in mechanic."""
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
    Helper for verifying error responses.
    
    Args:
        response: Response from TestClient
        expected_status: Expected status code
        expected_detail: Expected error detail
    """
    assert response.status_code == expected_status, \
        f"Expected {expected_status}, got {response.status_code}. Body: {response.text}"
    
    body = response.json()
    assert "detail" in body, f"Response doesn't contain 'detail'. Body: {body}"
    assert body["detail"] == expected_detail, \
        f"Expected detail '{expected_detail}', got '{body['detail']}'"


def assert_success_response(response, expected_status: int = 200):
    """
    Helper for verifying success responses.
    
    Args:
        response: Response from TestClient
        expected_status: Expected status code (default 200)
    
    Returns:
        Decoded JSON from response
    """
    assert response.status_code == expected_status, \
        f"Expected {expected_status}, got {response.status_code}. Body: {response.text}"
    
    return response.json()


class ClientHelper:
    """Helper for operations on clients"""
    
    BASE_URL = "/api/v1/clients"
    
    @staticmethod
    def create_client(
        client: TestClient,
        name: str = "Jan",
        last_name: str = "Kowalski",
        phone: str = None,
        pesel: str = None
    ) -> Dict[str, Any]:
        """
        Creates a client through API.
        
        Returns:
            Dict with keys: response, status_code, data (if success)
        """
        payload = {
            "name": name,
            "last_name": last_name
        }
        if phone:
            payload["phone"] = phone
        if pesel:
            payload["pesel"] = pesel
        
        response = client.post(ClientHelper.BASE_URL, json=payload)
        
        result = {
            "response": response,
            "status_code": response.status_code,
            "payload": payload
        }
        
        if response.status_code == 201:
            result["data"] = response.json()
        
        return result
    
    @staticmethod
    def get_client(client: TestClient, client_id: int) -> Dict[str, Any]:
        """Gets a client by ID"""
        response = client.get(f"{ClientHelper.BASE_URL}/{client_id}")
        
        result = {
            "response": response,
            "status_code": response.status_code
        }
        
        if response.status_code == 200:
            result["data"] = response.json()
        
        return result
    
    @staticmethod
    def update_client(
        client: TestClient,
        client_id: int,
        **update_fields
    ) -> Dict[str, Any]:
        """Updates a client"""
        response = client.put(
            f"{ClientHelper.BASE_URL}/{client_id}",
            json=update_fields
        )
        
        result = {
            "response": response,
            "status_code": response.status_code
        }
        
        if response.status_code == 200:
            result["data"] = response.json()
        
        return result
    
    @staticmethod
    def delete_client(client: TestClient, client_id: int) -> Dict[str, Any]:
        """Deletes a client"""
        response = client.delete(f"{ClientHelper.BASE_URL}/{client_id}")
        
        return {
            "response": response,
            "status_code": response.status_code
        }

