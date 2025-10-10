import pytest
from fastapi.testclient import TestClient

from tests.fixtures.helpers import AuthHelper, ClientHelper
from tests.fixtures.factories import MechanicFactory, ClientFactory


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_authenticated_mechanic(client: TestClient):
    """Create and login mechanic"""
    mechanic_data = MechanicFactory.build()
    result = AuthHelper.register_and_login(
        client,
        email=mechanic_data["email"],
        name=mechanic_data["name"],
        password=mechanic_data["password"]
    )
    return result["user_data"]


def create_test_vehicle(client: TestClient, **overrides):
    """Create vehicle with default data"""
    client_result = ClientHelper.create_client(
        client,
        name=overrides.pop("client_name", "Jan"),
        last_name=overrides.pop("client_last_name", "Kowalski")
    )
    client_id = client_result["data"]["id"]
    
    default_data = {
        "mark": "Toyota",
        "model": "Corolla",
        "vin": "12345678901234567",
        "client_id": client_id
    }
    default_data.update(overrides)
    
    response = client.post("/api/v1/vehicles", json=default_data)
    return response


# ============================================================================
# TESTS FOR CREATING VEHICLE (CREATE)
# ============================================================================

@pytest.mark.api
@pytest.mark.vehicles
@pytest.mark.integration
class TestCreateVehicle:
    """Tests for POST /api/v1/vehicles"""
    
    def test_create_vehicle_with_existing_client(self, client: TestClient):
        """
        GIVEN: Logged in mechanic and existing client
        WHEN: POST /vehicles z client_id
        THEN: Status 201, returned vehicle_id
        """
        # Arrange
        create_authenticated_mechanic(client)
        client_result = ClientHelper.create_client(client)
        client_id = client_result["data"]["id"]
        
        # Act - create vehicle
        response = client.post("/api/v1/vehicles", json={
            "mark": "Toyota",
            "model": "Corolla",
            "vin": "12345678901234567",
            "client_id": client_id
        })
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert "vehicle_id" in data
        assert isinstance(data["vehicle_id"], int)
    
    def test_create_vehicle_with_new_client(self, client: TestClient):
        """Test creating vehicle with new client (nested create)"""
        # Arrange
        create_authenticated_mechanic(client)
        
        # Act 
        response = client.post("/api/v1/vehicles", json={
            "mark": "BMW",
            "model": "X5",
            "vin": "98765432109876543",
            "client": {
                "name": "Anna",
                "last_name": "Nowak",
                "phone": "987654321"
            }
        })
        
        # Assert
        assert response.status_code == 201
        assert "vehicle_id" in response.json()
    
    def test_create_vehicle_without_vin(self, client: TestClient):
        """Test creating vehicle without VIN (optional)"""
        # Arrange
        create_authenticated_mechanic(client)
        client_result = ClientHelper.create_client(client)
        
        # Act
        response = client.post("/api/v1/vehicles", json={
            "mark": "Ford",
            "model": "Focus",
            "client_id": client_result["data"]["id"]
        })
        
        # Assert
        assert response.status_code == 201
    
    def test_create_vehicle_with_valid_vin(self, client: TestClient):
        """Test valid VIN (17 characters)"""
        # Arrange
        create_authenticated_mechanic(client)
        client_result = ClientHelper.create_client(client)
        
        # Act 
        response = client.post("/api/v1/vehicles", json={
            "mark": "Audi",
            "model": "A4",
            "vin": "WAUZZZ8E09A123456",  # 17 characters
            "client_id": client_result["data"]["id"]
        })
        
        # Assert
        assert response.status_code == 201


# ============================================================================
# TESTS FOR VALIDATION
# ============================================================================

@pytest.mark.api
@pytest.mark.vehicles
@pytest.mark.integration
class TestVehicleValidation:
    """Tests for validation of vehicle data"""
    
    def test_create_vehicle_missing_mark(self, client: TestClient):
        """Test missing required field 'mark'"""
        # Arrange
        create_authenticated_mechanic(client)
        client_result = ClientHelper.create_client(client)
        
        # Act - missing mark
        response = client.post("/api/v1/vehicles", json={
            "model": "Corolla",
            "client_id": client_result["data"]["id"]
        })
        
        # Assert
        assert response.status_code == 422
    
    def test_create_vehicle_missing_model(self, client: TestClient):
        """Test missing required field 'model'"""
        # Arrange
        create_authenticated_mechanic(client)
        client_result = ClientHelper.create_client(client)
        
        # Act
        response = client.post("/api/v1/vehicles", json={
            "mark": "Toyota",
            "client_id": client_result["data"]["id"]
        })
        
        # Assert
        assert response.status_code == 422
    
    def test_create_vehicle_without_client_data(self, client: TestClient):
        """Test missing client_id and client (both required)"""
        # Arrange
        create_authenticated_mechanic(client)
        
        # Act - missing client_id and client
        response = client.post("/api/v1/vehicles", json={
            "mark": "Toyota",
            "model": "Corolla"
        })
        
        # Assert
        assert response.status_code == 400
        assert "Client data or client_id must be provided" in response.json()["detail"]
    
    def test_create_vehicle_vin_too_short(self, client: TestClient):
        """Test VIN shorter than 17 characters"""
        # Arrange
        create_authenticated_mechanic(client)
        client_result = ClientHelper.create_client(client)
        
        # Act - VIN 16 characters
        response = client.post("/api/v1/vehicles", json={
            "mark": "Toyota",
            "model": "Corolla",
            "vin": "1234567890123456",  # 16 characters
            "client_id": client_result["data"]["id"]
        })
        
        # Assert
        assert response.status_code == 422
    
    def test_create_vehicle_vin_too_long(self, client: TestClient):
        """Test VIN longer than 17 characters"""
        # Arrange
        create_authenticated_mechanic(client)
        client_result = ClientHelper.create_client(client)
        
        # Act - VIN 18 characters
        response = client.post("/api/v1/vehicles", json={
            "mark": "Toyota",
            "model": "Corolla",
            "vin": "123456789012345678",  # 18 characters
            "client_id": client_result["data"]["id"]
        })
        
        # Assert
        assert response.status_code == 422
    
    @pytest.mark.parametrize("vin", [
        "12345678901234567",  # Valid
        "ABCDEFGHIJKLMNOPQ",  # Letters
        "ABC123DEF456GHI78",  # Mixed
        "!@#$%^&*()_+{}[]<",  # Special characters (if allowed)
    ])
    def test_create_vehicle_various_vin_formats(self, client: TestClient, vin: str):
        """Test different VIN formats (all 17 characters)"""
        # Arrange
        create_authenticated_mechanic(client)
        client_result = ClientHelper.create_client(client)
        
        # Act
        response = client.post("/api/v1/vehicles", json={
            "mark": "Test",
            "model": "Car",
            "vin": vin,
            "client_id": client_result["data"]["id"]
        })
        
        # Assert - all should be accepted (17 characters)
        assert response.status_code == 201


# ============================================================================
# TESTS FOR GETTING VEHICLE (READ)
# ============================================================================

@pytest.mark.api
@pytest.mark.vehicles
@pytest.mark.integration
class TestGetVehicle:
    """Tests for GET /api/v1/vehicles/{vehicle_id}"""
    
    def test_get_vehicle_success(self, client: TestClient):
        """Test getting vehicle details"""
        # Arrange
        create_authenticated_mechanic(client)
        create_response = create_test_vehicle(client)
        vehicle_id = create_response.json()["vehicle_id"]
        
        # Act
        response = client.get(f"/api/v1/vehicles/{vehicle_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == vehicle_id
        assert data["mark"] == "Toyota"
        assert data["model"] == "Corolla"
        assert "client" in data
    
    def test_get_vehicle_not_found(self, client: TestClient):
        """Test getting non-existent vehicle"""
        # Arrange
        create_authenticated_mechanic(client)
        
        # Act
        response = client.get("/api/v1/vehicles/99999")
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Vehicle not found"
    
    def test_get_vehicle_with_vin(self, client: TestClient):
        """Test that VIN is returned in the response"""
        # Arrange
        create_authenticated_mechanic(client)
        vin = "WAUZZZ8E09A123456"
        response = create_test_vehicle(client, vin=vin)
        vehicle_id = response.json()["vehicle_id"]
        
        # Act
        get_response = client.get(f"/api/v1/vehicles/{vehicle_id}")
        
        # Assert
        assert get_response.status_code == 200
        assert get_response.json()["vin"] == vin


# ============================================================================
# TESTS FOR UPDATING VEHICLE (UPDATE)
# ============================================================================

@pytest.mark.api
@pytest.mark.vehicles
@pytest.mark.integration
class TestUpdateVehicle:
    """Tests for PATCH /api/v1/vehicles/{vehicle_id}"""
    
    def test_update_vehicle_mark(self, client: TestClient):
        """Test updating vehicle mark"""
        # Arrange
        create_authenticated_mechanic(client)
        create_response = create_test_vehicle(client)
        vehicle_id = create_response.json()["vehicle_id"]
        
        # Act
        response = client.patch(
            f"/api/v1/vehicles/{vehicle_id}",
            json={"mark": "Honda"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["mark"] == "Honda"
        assert data["model"] == "Corolla"  # Other fields remain unchanged
    
    def test_update_vehicle_model(self, client: TestClient):
        """Test updating model"""
        # Arrange
        create_authenticated_mechanic(client)
        create_response = create_test_vehicle(client)
        vehicle_id = create_response.json()["vehicle_id"]
        
        # Act
        response = client.patch(
            f"/api/v1/vehicles/{vehicle_id}",
            json={"model": "Camry"}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["model"] == "Camry"
    
    def test_update_vehicle_vin(self, client: TestClient):
        """Test updating VIN"""
        # Arrange
        create_authenticated_mechanic(client)
        create_response = create_test_vehicle(client)
        vehicle_id = create_response.json()["vehicle_id"]
        new_vin = "NEWVIN12345678901"
        
        # Act
        response = client.patch(
            f"/api/v1/vehicles/{vehicle_id}",
            json={"vin": new_vin}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["vin"] == new_vin
    
    def test_update_vehicle_multiple_fields(self, client: TestClient):
        """Test updating multiple fields"""
        # Arrange
        create_authenticated_mechanic(client)
        create_response = create_test_vehicle(client)
        vehicle_id = create_response.json()["vehicle_id"]
        
        # Act
        response = client.patch(
            f"/api/v1/vehicles/{vehicle_id}",
            json={
                "mark": "BMW",
                "model": "320i",
                "vin": "NEWVIN12345678999"
            }
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["mark"] == "BMW"
        assert data["model"] == "320i"
        assert data["vin"] == "NEWVIN12345678999"
    
    def test_update_vehicle_not_found(self, client: TestClient):
        """Test updating non-existent vehicle"""
        # Arrange
        create_authenticated_mechanic(client)
        
        # Act
        response = client.patch(
            "/api/v1/vehicles/99999",
            json={"mark": "Test"}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Vehicle not found"
    
    def test_update_vehicle_invalid_vin_length(self, client: TestClient):
        """Test updating with invalid VIN"""
        # Arrange
        create_authenticated_mechanic(client)
        create_response = create_test_vehicle(client)
        vehicle_id = create_response.json()["vehicle_id"]
        
        # Act - VIN too short
        response = client.patch(
            f"/api/v1/vehicles/{vehicle_id}",
            json={"vin": "SHORT"}
        )
        
        # Assert
        assert response.status_code == 422


# ============================================================================
# TESTS FOR DELETING VEHICLE (DELETE)
# ============================================================================

@pytest.mark.api
@pytest.mark.vehicles
@pytest.mark.integration
class TestDeleteVehicle:
    """Tests for DELETE /api/v1/vehicles/{vehicle_id}"""
    
    def test_delete_vehicle_success(self, client: TestClient):
        """Test deleting vehicle"""
        # Arrange
        create_authenticated_mechanic(client)
        create_response = create_test_vehicle(client)
        vehicle_id = create_response.json()["vehicle_id"]
        
        # Act
        response = client.delete(f"/api/v1/vehicles/{vehicle_id}")
        
        # Assert
        assert response.status_code == 204
        
        # Check if really deleted
        get_response = client.get(f"/api/v1/vehicles/{vehicle_id}")
        assert get_response.status_code == 404
    
    def test_delete_vehicle_not_found(self, client: TestClient):
        """Test deleting non-existent vehicle"""
        # Arrange
        create_authenticated_mechanic(client)
        
        # Act
        response = client.delete("/api/v1/vehicles/99999")
        
        # Assert
        assert response.status_code == 404
    
    def test_delete_vehicle_idempotent(self, client: TestClient):
        """Test idempotency of DELETE"""
        # Arrange
        create_authenticated_mechanic(client)
        create_response = create_test_vehicle(client)
        vehicle_id = create_response.json()["vehicle_id"]
        
        # Act
        response1 = client.delete(f"/api/v1/vehicles/{vehicle_id}")
        response2 = client.delete(f"/api/v1/vehicles/{vehicle_id}")
        
        # Assert
        assert response1.status_code == 204
        assert response2.status_code == 404


# ============================================================================
# TESTS FOR RECENTLY VIEWED VEHICLES
# ============================================================================

@pytest.mark.api
@pytest.mark.vehicles
@pytest.mark.integration
class TestRecentlyViewedVehicles:
    """Tests for GET /api/v1/vehicles/recent"""
    
    def test_get_recently_viewed_empty(self, client: TestClient):
        """Test empty list of recently viewed"""
        # Arrange
        create_authenticated_mechanic(client)
        
        # Act
        response = client.get("/api/v1/vehicles/recent")
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert result == []
    
    def test_get_recently_viewed_after_viewing_vehicle(self, client: TestClient):
        """Test that vehicle appears after it is viewed"""
        # Arrange
        create_authenticated_mechanic(client)
        create_response = create_test_vehicle(client)
        vehicle_id = create_response.json()["vehicle_id"]
        
        # Act - view vehicle (this should update last_view)
        client.get(f"/api/v1/vehicles/{vehicle_id}")
        
        # Get recently viewed
        response = client.get("/api/v1/vehicles/recent?page=1&size=8")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["id"] == vehicle_id
    
    def test_recently_viewed_limit_five(self, client: TestClient):
        """Test that maximum 5 vehicles are returned"""
        # Arrange
        create_authenticated_mechanic(client)
        
        # Create and view 10 vehicles
        for i in range(10):
            create_response = create_test_vehicle(
                client,
                client_name=f"Client{i}",
                client_last_name=f"Last{i}",
                vin=f"VIN{i:011d}123"  # Unique VIN (17 characters: 3+11+3)
            )
            assert create_response.status_code == 201
            vehicle_id = create_response.json()["vehicle_id"]
            client.get(f"/api/v1/vehicles/{vehicle_id}")
        
        # Act - page 1 size 5
        response_page1 = client.get("/api/v1/vehicles/recent?page=1&size=5")
        response_page2 = client.get("/api/v1/vehicles/recent?page=2&size=5")
        response_page3 = client.get("/api/v1/vehicles/recent?page=3&size=5")
        
        # Assert
        assert response_page1.status_code == 200
        assert response_page2.status_code == 200
        assert response_page3.status_code == 200
        data_page1 = response_page1.json()
        data_page2 = response_page2.json()
        data_page3 = response_page3.json()
        assert len(data_page1) == 5
        assert len(data_page2) == 5
        assert len(data_page3) == 0


# ============================================================================
# TESTS FOR AUTHORIZATION
# ============================================================================

@pytest.mark.api
@pytest.mark.vehicles
@pytest.mark.integration
class TestVehicleAuthorization:
    """Tests for authorization - requires login"""
    
    def test_create_vehicle_without_auth(self, client: TestClient):
        """Test creating vehicle without login"""
        # Act
        response = client.post("/api/v1/vehicles", json={
            "mark": "Test",
            "model": "Car",
            "client_id": 1
        })
        
        # Assert
        assert response.status_code == 401
    
    def test_get_vehicle_without_auth(self, client: TestClient):
        """Test getting vehicle without login"""
        # Act
        response = client.get("/api/v1/vehicles/1")
        
        # Assert
        assert response.status_code == 401
    
    def test_update_vehicle_without_auth(self, client: TestClient):
        """Test updating vehicle without login"""
        # Act
        response = client.patch("/api/v1/vehicles/1", json={"mark": "Test"})
        
        # Assert
        assert response.status_code == 401
    
    def test_delete_vehicle_without_auth(self, client: TestClient):
        """Test deleting vehicle without login"""
        # Act
        response = client.delete("/api/v1/vehicles/1")
        
        # Assert
        assert response.status_code == 401
    
    def test_get_recent_without_auth(self, client: TestClient):
        """Test getting recently viewed vehicles without login"""
        # Act
        response = client.get("/api/v1/vehicles/recent")
        
        # Assert
        assert response.status_code == 401


# ============================================================================
# TESTS FOR EDGE CASES
# ============================================================================

@pytest.mark.api
@pytest.mark.vehicles
@pytest.mark.integration
class TestVehicleEdgeCases:
    """Tests for edge cases"""
    
    def test_create_vehicle_very_long_mark(self, client: TestClient):
        """Test very long mark"""
        # Arrange
        create_authenticated_mechanic(client)
        client_result = ClientHelper.create_client(client)
        long_mark = "A" * 500
        
        # Act
        response = client.post("/api/v1/vehicles", json={
            "mark": long_mark,
            "model": "Test",
            "client_id": client_result["data"]["id"]
        })
        
        # Assert    
        assert response.status_code in [201, 422]
    
    def test_create_vehicle_special_characters_in_mark(self, client: TestClient):
        """Test special characters in mark"""
        # Arrange
        create_authenticated_mechanic(client)
        client_result = ClientHelper.create_client(client)
        
        # Act
        response = client.post("/api/v1/vehicles", json={
            "mark": "Mercedes-Benz",  
            "model": "C-Class",
            "client_id": client_result["data"]["id"]
        })
        
        # Assert
        assert response.status_code == 201
    
    def test_create_multiple_vehicles_for_same_client(self, client: TestClient):
        """Test creating multiple vehicles for the same client"""
        # Arrange
        create_authenticated_mechanic(client)
        client_result = ClientHelper.create_client(client)
        client_id = client_result["data"]["id"]
        
        # Act 
        vehicle_ids = []
        for i in range(3):
            response = client.post("/api/v1/vehicles", json={
                "mark": f"Brand{i}",
                "model": f"Model{i}",
                "vin": f"VIN{i:011d}123",  
                "client_id": client_id
            })
            assert response.status_code == 201
            vehicle_ids.append(response.json()["vehicle_id"])
        
        # Assert 
        assert len(vehicle_ids) == 3
        assert len(set(vehicle_ids)) == 3 
    
    def test_update_vehicle_with_empty_data(self, client: TestClient):
        """Test updating with no data"""
        # Arrange
        create_authenticated_mechanic(client)
        create_response = create_test_vehicle(client)
        vehicle_id = create_response.json()["vehicle_id"]
        
        # Act - empty data
        response = client.patch(f"/api/v1/vehicles/{vehicle_id}", json={})
        
        # Assert 
        assert response.status_code == 200
    
    def test_create_vehicle_with_nonexistent_client_id(self, client: TestClient):
        """Test creating vehicle with nonexistent client_id"""
        # Arrange
        create_authenticated_mechanic(client)
        
        # Act
        response = client.post("/api/v1/vehicles", json={
            "mark": "Toyota",
            "model": "Corolla",
            "client_id": 99999  
        })
        
        # Assert 
        assert response.status_code == 201  # TODO: Dodać walidację client_id w service!
    
    def test_create_vehicle_with_both_client_and_client_id(self, client: TestClient):
        """Test when both client and client_id are provided"""
        # Arrange
        create_authenticated_mechanic(client)
        client_result = ClientHelper.create_client(client)
        
        # Act 
        response = client.post("/api/v1/vehicles", json={
            "mark": "Toyota",
            "model": "Corolla",
            "client_id": client_result["data"]["id"],
            "client": {
                "name": "Test",
                "last_name": "User"
            }
        })
        
        # Assert 
        assert response.status_code == 201

