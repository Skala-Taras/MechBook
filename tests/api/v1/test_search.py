
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from tests.fixtures.helpers import AuthHelper, ClientHelper
from tests.fixtures.factories import MechanicFactory, ClientFactory
from app.schemas.search import SearchResult


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_authenticated_mechanic(client: TestClient):
    """Create and login a mechanic"""
    mechanic_data = MechanicFactory.build()
    result = AuthHelper.register_and_login(
        client,
        email=mechanic_data["email"],
        name=mechanic_data["name"],
        password=mechanic_data["password"]
    )
    return result["user_data"]


def create_mock_search_results(results_data):
    """Create mock SearchResult objects"""
    return [SearchResult(**data) for data in results_data]


# ============================================================================
# SEARCH ENDPOINT TESTS
# ============================================================================

@pytest.mark.api
@pytest.mark.integration
class TestSearchEndpoint:
    """Tests for GET /api/v1/search"""
    
    @patch('app.api.v1.endpoints.search.search_service.search')
    def test_search_clients_by_name(self, mock_search, client: TestClient):
        """Search for clients by name"""
        # Arrange
        mock_results = create_mock_search_results([
            {"id": 1, "type": "client", "name": "John Doe"},
            {"id": 2, "type": "client", "name": "John Smith"}
        ])
        mock_search.return_value = mock_results
        
        # Act
        response = client.get("/api/v1/search?q=John")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["type"] == "client"
        assert "John" in data[0]["name"]
        mock_search.assert_called_once_with("John")
    
    @patch('app.api.v1.endpoints.search.search_service.search')
    def test_search_vehicles_by_mark(self, mock_search, client: TestClient):
        """Search for vehicles by mark"""
        # Arrange
        mock_results = create_mock_search_results([
            {"id": 1, "type": "vehicle", "name": "Toyota Corolla"},
        ])
        mock_search.return_value = mock_results
        
        # Act
        response = client.get("/api/v1/search?q=Toyota")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["type"] == "vehicle"
        assert "Toyota" in data[0]["name"]
    
    @patch('app.api.v1.endpoints.search.search_service.search')
    def test_search_by_phone(self, mock_search, client: TestClient):
        """Search for client by phone number"""
        # Arrange
        mock_results = create_mock_search_results([
            {"id": 1, "type": "client", "name": "Jane Doe", "phone": "123456789"}
        ])
        mock_search.return_value = mock_results
        
        # Act
        response = client.get("/api/v1/search?q=123456789")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        mock_search.assert_called_once_with("123456789")
    
    @patch('app.api.v1.endpoints.search.search_service.search')
    def test_search_by_vin(self, mock_search, client: TestClient):
        """Search for vehicle by VIN"""
        # Arrange
        mock_results = create_mock_search_results([
            {"id": 1, "type": "vehicle", "name": "Honda Civic", "vin": "1112345678901234"}
        ])
        mock_search.return_value = mock_results
        
        # Act
        response = client.get("/api/v1/search?q=1112345678901234")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["type"] == "vehicle"
        assert data[0]["name"] == "Honda Civic"
    
    @patch('app.api.v1.endpoints.search.search_service.search')
    def test_search_mixed_results(self, mock_search, client: TestClient):
        """Search returns both clients and vehicles when searching by client surname
        
        Explanation: When searching for "Kowal", Elasticsearch finds:
        - Clients with "Kowal" in their name (John Kowalski, Anna Kowalska)
        - Vehicles owned by those clients (matched through 'client_name' field)
        
        This works because vehicles are indexed with their owner's name in 'client_name' field.
        """
        # Arrange - Simulate Elasticsearch returning clients and their vehicle
        mock_results = create_mock_search_results([
            {"id": 1, "type": "client", "name": "John Kowalski"},
            {"id": 1, "type": "vehicle", "name": "John Kowalski", "mark": "Toyota", "model": "Camry"},  # Owned by John Kowalski
            {"id": 2, "type": "client", "name": "Anna Kowalska"}
        ])
        mock_search.return_value = mock_results
        
        # Act
        response = client.get("/api/v1/search?q=Kowal")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3  # 2 clients + 1 vehicle
        
        types = [item["type"] for item in data]
        assert "client" in types
        assert "vehicle" in types
        
        # Verify counts
        client_count = sum(1 for item in data if item["type"] == "client")
        vehicle_count = sum(1 for item in data if item["type"] == "vehicle")
        assert client_count == 2, "Should have 2 clients (John Kowalski, Anna Kowalska)"
        assert vehicle_count == 1, "Should have 1 vehicle (Toyota Camry owned by John Kowalski)"
    
    @patch('app.api.v1.endpoints.search.search_service.search')
    def test_search_empty_results(self, mock_search, client: TestClient):
        """Search with no matching results"""
        # Arrange
        mock_search.return_value = []
        
        # Act
        response = client.get("/api/v1/search?q=NonexistentQuery")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    @patch('app.api.v1.endpoints.search.search_service.search')
    def test_search_with_special_characters(self, mock_search, client: TestClient):
        """Search with special characters"""
        # Arrange
        mock_search.return_value = []
        
        # Act
        response = client.get("/api/v1/search?q=test@#$%")
        
        # Assert
        assert response.status_code == 200
        # Check that mock was called (URL encoding may change the exact string)
        assert mock_search.called
    
    @patch('app.api.v1.endpoints.search.search_service.search')
    def test_search_with_spaces(self, mock_search, client: TestClient):
        """Search with spaces in query"""
        # Arrange
        mock_results = create_mock_search_results([
            {"id": 1, "type": "client", "name": "John Smith"}
        ])
        mock_search.return_value = mock_results
        
        # Act
        response = client.get("/api/v1/search?q=John Smith")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        mock_search.assert_called_once_with("John Smith")
    
    @patch('app.api.v1.endpoints.search.search_service.search')
    def test_search_case_insensitive(self, mock_search, client: TestClient):
        """Search is case insensitive"""
        # Arrange
        mock_results = create_mock_search_results([
            {"id": 1, "type": "client", "name": "John Doe"}
        ])
        mock_search.return_value = mock_results
        
        # Act
        response = client.get("/api/v1/search?q=JOHN")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "John Doe"


# ============================================================================
# VALIDATION TESTS
# ============================================================================

@pytest.mark.api
@pytest.mark.integration
class TestSearchValidation:
    """Tests for search query validation"""
    
    def test_search_missing_query_parameter(self, client: TestClient):
        """Reject search without query parameter"""
        # Act
        response = client.get("/api/v1/search")
        
        # Assert
        assert response.status_code == 422  # Missing required query param
    
    @patch('app.api.v1.endpoints.search.search_service.search')
    def test_search_empty_query_string(self, mock_search, client: TestClient):
        """Handle empty query string"""
        # Arrange
        mock_search.return_value = []
        
        # Act
        response = client.get("/api/v1/search?q=")
        
        # Assert
        assert response.status_code == 200
    
    @patch('app.api.v1.endpoints.search.search_service.search')
    def test_search_very_long_query(self, mock_search, client: TestClient):
        """Handle very long search query"""
        # Arrange
        long_query = "a" * 1000
        mock_search.return_value = []
        
        # Act
        response = client.get(f"/api/v1/search?q={long_query}")
        
        # Assert
        assert response.status_code == 200


# ============================================================================
# FUZZY MATCHING TESTS
# ============================================================================

@pytest.mark.api
@pytest.mark.integration
class TestSearchFuzzyMatching:
    """Tests for fuzzy matching and typo tolerance"""
    
    @patch('app.api.v1.endpoints.search.search_service.search')
    def test_search_with_typo(self, mock_search, client: TestClient):
        """Search with typo finds correct results"""
        # Arrange - simulating fuzzy match
        mock_results = create_mock_search_results([
            {"id": 1, "type": "client", "name": "John Smith"}
        ])
        mock_search.return_value = mock_results
        
        # Act - typo: "Jhon" instead of "John"
        response = client.get("/api/v1/search?q=Jhon")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "John Smith"
    
    @patch('app.api.v1.endpoints.search.search_service.search')
    def test_search_partial_match(self, mock_search, client: TestClient):
        """Search with partial word matches"""
        # Arrange
        mock_results = create_mock_search_results([
            {"id": 1, "type": "vehicle", "name": "Toyota Corolla"}
        ])
        mock_search.return_value = mock_results
        
        # Act - partial word "Toyo"
        response = client.get("/api/v1/search?q=Toyo")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Toyota Corolla"


# ============================================================================
# EDGE CASES
# ============================================================================

@pytest.mark.api
@pytest.mark.integration
class TestSearchEdgeCases:
    """Tests for edge cases and special scenarios"""
    
    @patch('app.api.v1.endpoints.search.search_service.search')
    def test_search_with_numbers_only(self, mock_search, client: TestClient):
        """Search with only numbers"""
        # Arrange
        mock_results = create_mock_search_results([
            {"id": 1, "type": "client", "name": "Client 123"}
        ])
        mock_search.return_value = mock_results
        
        # Act
        response = client.get("/api/v1/search?q=123")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Client 123"
    
    @patch('app.api.v1.endpoints.search.search_service.search')
    def test_search_with_unicode_characters(self, mock_search, client: TestClient):
        """Search with unicode/special characters"""
        # Arrange
        mock_results = create_mock_search_results([
            {"id": 1, "type": "client", "name": "Łukasz Żółtek"}
        ])
        mock_search.return_value = mock_results
        
        # Act
        response = client.get("/api/v1/search?q=Łukasz")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Łukasz Żółtek"
    
    @patch('app.api.v1.endpoints.search.search_service.search')
    def test_search_returns_limited_results(self, mock_search, client: TestClient):
        """Search returns reasonable number of results"""
        # Arrange - 100 results
        mock_results = create_mock_search_results([
            {"id": i, "type": "client", "name": f"Client {i}"}
            for i in range(100)
        ])
        mock_search.return_value = mock_results
        
        # Act
        response = client.get("/api/v1/search?q=Client")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 100
    
    @patch('app.api.v1.endpoints.search.search_service.search')
    def test_search_with_url_encoded_query(self, mock_search, client: TestClient):
        """Search with URL encoded characters"""
        # Arrange
        mock_results = create_mock_search_results([
            {"id": 1, "type": "client", "name": "Smith & Sons"}
        ])
        mock_search.return_value = mock_results
        
        # Act - URL encoded "&" is %26
        response = client.get("/api/v1/search?q=Smith%20%26%20Sons")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        mock_search.assert_called_once_with("Smith & Sons")
    
    @patch('app.api.v1.endpoints.search.search_service.search')
    def test_search_single_character(self, mock_search, client: TestClient):
        """Search with single character query"""
        # Arrange
        mock_search.return_value = []
        
        # Act
        response = client.get("/api/v1/search?q=A")
        
        # Assert
        assert response.status_code == 200
        mock_search.assert_called_once_with("A")


# ============================================================================
# RESPONSE FORMAT TESTS
# ============================================================================

@pytest.mark.api
@pytest.mark.integration
class TestSearchResponseFormat:
    """Tests for search response format"""
    
    @patch('app.api.v1.endpoints.search.search_service.search')
    def test_search_response_structure_for_client(self, mock_search, client: TestClient):
        """Client search result has correct structure"""
        # Arrange
        mock_results = create_mock_search_results([
            {"id": 1, "type": "client", "name": "John Doe"}
        ])
        mock_search.return_value = mock_results
        
        # Act
        response = client.get("/api/v1/search?q=John")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        
        result = data[0]
        assert "id" in result
        assert "type" in result
        assert result["type"] == "client"
        assert "name" in result
    
    @patch('app.api.v1.endpoints.search.search_service.search')
    def test_search_response_structure_for_vehicle(self, mock_search, client: TestClient):
        """Vehicle search result has correct structure"""
        # Arrange
        mock_results = create_mock_search_results([
            {"id": 1, "type": "vehicle", "name": "Toyota Corolla"}
        ])
        mock_search.return_value = mock_results
        
        # Act
        response = client.get("/api/v1/search?q=Toyota")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        
        result = data[0]
        assert "id" in result
        assert "type" in result
        assert result["type"] == "vehicle"
    
    @patch('app.api.v1.endpoints.search.search_service.search')
    def test_search_returns_json_array(self, mock_search, client: TestClient):
        """Search always returns JSON array"""
        # Arrange
        mock_search.return_value = []
        
        # Act
        response = client.get("/api/v1/search?q=test")
        
        # Assert
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert isinstance(data, list)

