import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from tests.fixtures.helpers import AuthHelper, ClientHelper
from tests.fixtures.factories import MechanicFactory, ClientFactory


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_authenticated_mechanic(client: TestClient):
    """Creates and logs in mechanic"""
    mechanic_data = MechanicFactory.build()
    result = AuthHelper.register_and_login(
        client,
        email=mechanic_data["email"],
        name=mechanic_data["name"],
        password=mechanic_data["password"]
    )
    return result["user_data"]


def create_test_vehicle(client: TestClient):
    """Creates vehicle with client and returns vehicle_id"""
    
    client_result = ClientHelper.create_client(client, name="Jan", last_name="Kowalski")
    client_id = client_result["data"]["id"]

    response = client.post("/api/v1/vehicles", json={
        "mark": "Toyota",
        "model": "Corolla",
        "vin": "12345678901234567",
        "client_id": client_id
    })
    assert response.status_code == 201
    return response.json()["vehicle_id"]


def create_test_repair(client: TestClient, vehicle_id: int, **overrides):
    """Creates repair for vehicle"""
    default_data = {
        "name": "Wymiana oleju",
        "repair_description": "Wymiana oleju silnikowego",
        "price": 250.50,
        "repair_date": datetime.utcnow().isoformat()
    }
    default_data.update(overrides)
    
    response = client.post(
        f"/api/v1/vehicles/{vehicle_id}/repairs",
        json=default_data
    )
    return response


# ============================================================================
# TESTS FOR CREATING REPAIR (CREATE)
# ============================================================================

@pytest.mark.api
@pytest.mark.integration
class TestCreateRepair:
    """Tests for POST /api/v1/vehicles/{vehicle_id}/repairs"""
    
    def test_create_repair_success(self, client: TestClient):
        """
        GIVEN: Logged in mechanic, vehicle and repair data
        WHEN: POST /vehicles/{id}/repairs
        THEN: Status 201, returned repair data with ID
        """
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        repair_data = {
            "name": "Wymiana oleju",
            "repair_description": "Wymiana oleju silnikowego 5W-30",
            "price": 250.50,
            "repair_date": datetime.utcnow().isoformat()
        }
        
        # Act - create repair
        response = client.post(
            f"/api/v1/vehicles/{vehicle_id}/repairs",
            json=repair_data
        )
        
        # Assert - check response
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Wymiana oleju"
        assert data["price"] == 250.50
        assert "id" in data
        assert data["vehicle"]["id"] == vehicle_id
    
    def test_create_repair_with_optional_fields_only(self, client: TestClient):
        """Test creating repair with only required fields"""
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        
        # Act - only required fields
        response = client.post(
            f"/api/v1/vehicles/{vehicle_id}/repairs",
            json={
                "name": "Przegląd",
                "repair_date": datetime.utcnow().isoformat()
            }
        )
        
        # Assert - check response
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Przegląd"
        # price and description can be None or have default values
    
    def test_create_repair_with_past_date(self, client: TestClient):
        """Test creating repair with past date"""
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        past_date = (datetime.utcnow() - timedelta(days=30)).isoformat()
        
        # Act - create repair
        response = create_test_repair(client, vehicle_id, repair_date=past_date)
        
        # Assert - check response   
        assert response.status_code == 201
    
    def test_create_repair_with_future_date(self, client: TestClient):
        """Test creating repair with future date (planned)"""
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        future_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
        
        # Act
        response = create_test_repair(client, vehicle_id, repair_date=future_date)
        
        # Assert
        assert response.status_code == 201
    
    def test_create_repair_with_zero_price(self, client: TestClient):
        """Test repair with price 0 (guarantee)"""
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        
        # Act
        response = create_test_repair(client, vehicle_id, price=0.0)
        
        # Assert
        assert response.status_code == 201
        assert response.json()["price"] == 0.0
    
    def test_create_repair_with_high_price(self, client: TestClient):
        """Test repair with high price"""
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        
        # Act
        response = create_test_repair(client, vehicle_id, price=99999.99)
        
        # Assert
        assert response.status_code == 201
        assert response.json()["price"] == 99999.99


# ============================================================================
# TESTS FOR VALIDATION
# ============================================================================

@pytest.mark.api
@pytest.mark.integration
class TestRepairValidation:
    """Tests for validation of repair data"""
    
    def test_create_repair_missing_name(self, client: TestClient):
        """Test missing required field 'name'"""
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        
        # Act - missing name
        response = client.post(
            f"/api/v1/vehicles/{vehicle_id}/repairs",
            json={
                "repair_date": datetime.utcnow().isoformat()
            }
        )
        
        # Assert - check response
        assert response.status_code == 422
    
    def test_create_repair_missing_date(self, client: TestClient):
        """Test missing required field 'repair_date'"""
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        
        # Act
        response = client.post(
            f"/api/v1/vehicles/{vehicle_id}/repairs",
            json={"name": "Test"}
        )
        
        # Assert
        assert response.status_code == 422
    
    def test_create_repair_invalid_date_format(self, client: TestClient):
        """Test invalid date format"""
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        
        # Act
        response = client.post(
            f"/api/v1/vehicles/{vehicle_id}/repairs",
            json={
                "name": "Test",
                "repair_date": "not-a-date"
            }
        )
        
        # Assert
        assert response.status_code == 422
    
    def test_create_repair_negative_price(self, client: TestClient):
        """Test negative price"""
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        
        # Act
        response = create_test_repair(client, vehicle_id, price=-100.0)
        
        # Assert
        assert response.status_code in [201, 422]


# ============================================================================
# TESTS FOR GETTING REPAIRS (READ)
# ============================================================================

@pytest.mark.api
@pytest.mark.integration
class TestGetRepairs:
    """Tests for GET /api/v1/vehicles/{vehicle_id}/repairs"""
    
    def test_get_repairs_empty_list(self, client: TestClient):
        """Test getting repairs for vehicle without repairs"""
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        
        # Act
        response = client.get(f"/api/v1/vehicles/{vehicle_id}/repairs")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_repairs_list(self, client: TestClient):
        """Test getting list of repairs"""
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        
        # Act - create 3 repairs
        for i in range(3):
            create_test_repair(client, vehicle_id, name=f"Naprawa {i+1}")
        
        # Act - get repairs
        response = client.get(f"/api/v1/vehicles/{vehicle_id}/repairs")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("id" in repair for repair in data)
    
    def test_get_repairs_pagination_default(self, client: TestClient):
        """Test domyślnej paginacji (page=1, size=10)"""
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        
        # Utwórz 15 napraw
        for i in range(15):
            create_test_repair(client, vehicle_id, name=f"Naprawa {i+1}")
        
        # Act - domyślna paginacja
        response = client.get(f"/api/v1/vehicles/{vehicle_id}/repairs")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 10  # Domyślny size
    
    def test_get_repairs_pagination_custom(self, client: TestClient):
        """Test custom pagination"""
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        
        for i in range(10):
            create_test_repair(client, vehicle_id, name=f"Naprawa {i+1}")
        
        # Act - page=1, size=5
        response = client.get(f"/api/v1/vehicles/{vehicle_id}/repairs?page=1&size=5")
        
        # Assert
        assert response.status_code == 200
        assert len(response.json()) == 5
    
    def test_get_repairs_second_page(self, client: TestClient):
        """Test second page of results"""
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        
        for i in range(15):
            create_test_repair(client, vehicle_id)
        
        # Act
        response = client.get(f"/api/v1/vehicles/{vehicle_id}/repairs?page=2&size=10")
        
        # Assert
        assert response.status_code == 200
        assert len(response.json()) == 5  # Pozostałe 5 z 15


# ============================================================================
# TESTY POBIERANIA SZCZEGÓŁÓW NAPRAWY
# ============================================================================

@pytest.mark.api
@pytest.mark.integration
class TestGetRepairDetails:
    """Tests for GET /api/v1/vehicles/{vehicle_id}/repairs/{repair_id}"""
    
    def test_get_repair_details_success(self, client: TestClient):
        """Test getting repair details"""
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        create_response = create_test_repair(client, vehicle_id)
        repair_id = create_response.json()["id"]
        
        # Act
        response = client.get(f"/api/v1/vehicles/{vehicle_id}/repairs/{repair_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == repair_id
        assert data["name"] == "Wymiana oleju"
        assert "vehicle" in data
    
    def test_get_repair_details_not_found(self, client: TestClient):
        """Test getting non-existent repair"""
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        
        # Act
        response = client.get(f"/api/v1/vehicles/{vehicle_id}/repairs/99999")
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Repair not found"


# ============================================================================
# TESTS FOR UPDATING REPAIR (UPDATE)
# ============================================================================

@pytest.mark.api
@pytest.mark.integration
class TestUpdateRepair:
    """Tests for PATCH /api/v1/vehicles/{vehicle_id}/repairs/{repair_id}"""
    
    def test_update_repair_name(self, client: TestClient):
        """Test updating repair name"""
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        create_response = create_test_repair(client, vehicle_id)
        repair_id = create_response.json()["id"]
        
        # Act
        response = client.patch(
            f"/api/v1/vehicles/{vehicle_id}/repairs/{repair_id}",
            json={"name": "Wymiana płynów"}
        )
        
        # Assert
        assert response.status_code == 204
        
        # Check if it really changed
        get_response = client.get(f"/api/v1/vehicles/{vehicle_id}/repairs/{repair_id}")
        assert get_response.json()["name"] == "Wymiana płynów"
    
    def test_update_repair_price(self, client: TestClient):
        """Test updating price"""
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        create_response = create_test_repair(client, vehicle_id, price=100.0)
        repair_id = create_response.json()["id"]
        
        # Act
        response = client.patch(
            f"/api/v1/vehicles/{vehicle_id}/repairs/{repair_id}",
            json={"price": 350.75}
        )
        
        # Assert
        assert response.status_code == 204
        
        get_response = client.get(f"/api/v1/vehicles/{vehicle_id}/repairs/{repair_id}")
        assert get_response.json()["price"] == 350.75
    
    def test_update_repair_description(self, client: TestClient):
        """Test updating description"""
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        create_response = create_test_repair(client, vehicle_id)
        repair_id = create_response.json()["id"]
        
        # Act
        response = client.patch(
            f"/api/v1/vehicles/{vehicle_id}/repairs/{repair_id}",
            json={"repair_description": "Nowy szczegółowy opis naprawy"}
        )
        
        # Assert
        assert response.status_code == 204
    
    def test_update_repair_multiple_fields(self, client: TestClient):
        """Test updating multiple fields"""
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        create_response = create_test_repair(client, vehicle_id)
        repair_id = create_response.json()["id"]
        
        # Act
        response = client.patch(
            f"/api/v1/vehicles/{vehicle_id}/repairs/{repair_id}",
            json={
                "name": "Kompleksowa naprawa",
                "price": 1500.00,
                "repair_description": "Pełny zakres napraw"
            }
        )
        
        # Assert
        assert response.status_code == 204
        
        get_response = client.get(f"/api/v1/vehicles/{vehicle_id}/repairs/{repair_id}")
        data = get_response.json()
        assert data["name"] == "Kompleksowa naprawa"
        assert data["price"] == 1500.00
    
    def test_update_repair_not_found(self, client: TestClient):
        """Test updating non-existent repair"""
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        
        # Act
        response = client.patch(
            f"/api/v1/vehicles/{vehicle_id}/repairs/99999",
            json={"name": "Test"}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Repair not found"


# ============================================================================
# TESTS FOR DELETING REPAIR (DELETE)
# ============================================================================

@pytest.mark.api
@pytest.mark.integration
class TestDeleteRepair:
    """Tests for DELETE /api/v1/vehicles/{vehicle_id}/repairs/{repair_id}"""
    
    def test_delete_repair_success(self, client: TestClient):
        """Test deleting repair"""
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        create_response = create_test_repair(client, vehicle_id)
        repair_id = create_response.json()["id"]
        
        # Act
        response = client.delete(f"/api/v1/vehicles/{vehicle_id}/repairs/{repair_id}")
        
        # Assert
        assert response.status_code == 204
        get_response = client.get(f"/api/v1/vehicles/{vehicle_id}/repairs/{repair_id}")
        assert get_response.status_code == 404
    
    def test_delete_repair_not_found(self, client: TestClient):
        """Test deleting non-existent repair"""
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        
        # Act
        response = client.delete(f"/api/v1/vehicles/{vehicle_id}/repairs/99999")
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Repair not found"
    
    def test_delete_repair_idempotent(self, client: TestClient):
        """Test idempotency of DELETE (second call returns 404)"""
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        create_response = create_test_repair(client, vehicle_id)
        repair_id = create_response.json()["id"]
        
        # Act - first deletion
        response1 = client.delete(f"/api/v1/vehicles/{vehicle_id}/repairs/{repair_id}")
        # Second deletion
        response2 = client.delete(f"/api/v1/vehicles/{vehicle_id}/repairs/{repair_id}")
        
        # Assert
        assert response1.status_code == 204
        assert response2.status_code == 404


# ============================================================================
# TESTS FOR AUTHORIZATION
# ============================================================================

@pytest.mark.api
@pytest.mark.integration
class TestRepairAuthorization:
    """Tests for authorization - requires login"""
    
    def test_create_repair_without_auth(self, client: TestClient):
        """Test creating repair without login"""
        # Act - brak logowania
        response = client.post(
            "/api/v1/vehicles/1/repairs",
            json={
                "name": "Test",
                "repair_date": datetime.utcnow().isoformat()
            }
        )
        
        # Assert
        assert response.status_code == 401
    
    def test_get_repairs_without_auth(self, client: TestClient):
        """Test getting repairs without login"""
        # Act
        response = client.get("/api/v1/vehicles/1/repairs")
        
        # Assert
        assert response.status_code == 401
    
    def test_update_repair_without_auth(self, client: TestClient):
        """Test updating repair without login"""
        # Act
        response = client.patch(
            "/api/v1/vehicles/1/repairs/1",
            json={"name": "Test"}
        )
        
        # Assert
        assert response.status_code == 401
    
    def test_delete_repair_without_auth(self, client: TestClient):
        """Test deleting repair without login"""
        # Act
        response = client.delete("/api/v1/vehicles/1/repairs/1")
        
        # Assert
        assert response.status_code == 401


# ============================================================================
# TESTS FOR EDGE CASES
# ============================================================================

@pytest.mark.api
@pytest.mark.integration
class TestRepairEdgeCases:
    """Tests for edge cases"""
    
    def test_create_repair_very_long_name(self, client: TestClient):
        """Test very long repair name"""
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        long_name = "A" * 500
        
        # Act
        response = create_test_repair(client, vehicle_id, name=long_name)
        
        # Assert
        assert response.status_code == 201
    
    def test_create_repair_very_long_description(self, client: TestClient):
        """Test very long description"""
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        long_desc = "Lorem ipsum " * 1000
        
        # Act
        response = create_test_repair(
            client,
            vehicle_id,
            repair_description=long_desc
        )
        
        # Assert
        assert response.status_code == 201
    
    def test_create_multiple_repairs_for_same_vehicle(self, client: TestClient):
        """Test tworzenia wielu napraw dla tego samego pojazdu"""
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        
        # Act - utwórz 10 napraw
        repair_ids = []
        for i in range(10):
            response = create_test_repair(client, vehicle_id, name=f"Naprawa {i+1}")
            assert response.status_code == 201
            repair_ids.append(response.json()["id"])
        
        # Assert - wszystkie mają unikalne ID
        assert len(repair_ids) == 10
        assert len(set(repair_ids)) == 10
    
    def test_get_repairs_with_invalid_pagination(self, client: TestClient):
        """Test niepoprawnych parametrów paginacji"""
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        
        # Act - page=0 (może być błąd lub domyślnie 1)
        response = client.get(f"/api/v1/vehicles/{vehicle_id}/repairs?page=0")
        
        # Assert - zależy od implementacji, może być 200 lub 422
        assert response.status_code in [200, 422]
    
    def test_update_repair_with_empty_data(self, client: TestClient):
        """Test aktualizacji bez żadnych danych"""
        # Arrange
        create_authenticated_mechanic(client)
        vehicle_id = create_test_vehicle(client)
        create_response = create_test_repair(client, vehicle_id)
        repair_id = create_response.json()["id"]
        
        # Act - puste dane
        response = client.patch(
            f"/api/v1/vehicles/{vehicle_id}/repairs/{repair_id}",
            json={}
        )
        
        # Assert - powinno być OK (brak zmian)
        assert response.status_code == 204

