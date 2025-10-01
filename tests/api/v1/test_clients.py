"""
Kompletne testy dla endpointów klientów (/api/v1/clients).

Pokrycie:
- CRUD operations (Create, Read, Update, Delete)
- Walidacja danych (PESEL, wymagane pola)
- Duplikaty (name+last_name, phone, pesel)
- Autoryzacja (wymagany login)
- Formatowanie nazw (Title case)
- Edge cases
"""
import pytest
from fastapi.testclient import TestClient

from tests.fixtures.helpers import AuthHelper
from tests.fixtures.factories import MechanicFactory, ClientFactory


BASE_URL = "/api/v1/clients"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_authenticated_mechanic(client: TestClient):
    """Tworzy i loguje mechanika, zwraca jego dane"""
    mechanic_data = MechanicFactory.build()
    result = AuthHelper.register_and_login(
        client,
        email=mechanic_data["email"],
        name=mechanic_data["name"],
        password=mechanic_data["password"]
    )
    return result["user_data"]


def create_test_client(client: TestClient, **overrides):
    """Tworzy klienta przez API i zwraca odpowiedź"""
    default_data = {
        "name": "Jan",
        "last_name": "Kowalski",
        "phone": "123456789",
        "pesel": "12345678901"
    }
    default_data.update(overrides)
    
    response = client.post(BASE_URL, json=default_data)
    return response


# ============================================================================
# TESTY TWORZENIA KLIENTA (CREATE)
# ============================================================================

@pytest.mark.api
@pytest.mark.integration
class TestCreateClient:
    """Testy POST /api/v1/clients - tworzenie klienta"""
    
    def test_create_client_success(self, client: TestClient):
        """
        GIVEN: Zalogowany mechanik i poprawne dane klienta
        WHEN: POST /clients z danymi
        THEN: Status 201, zwrócone dane klienta z ID
        """
        # Arrange
        create_authenticated_mechanic(client)
        client_data = {
            "name": "Jan",
            "last_name": "Kowalski",
            "phone": "123456789",
            "pesel": "12345678901"
        }
        
        # Act
        response = client.post(BASE_URL, json=client_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Jan"
        assert data["last_name"] == "Kowalski"
        assert data["phone"] == "123456789"
        assert data["pesel"] == "12345678901"
        assert "id" in data
        assert isinstance(data["id"], int)
    
    def test_create_client_without_optional_fields(self, client: TestClient):
        """Test creating client without optional fields (phone, pesel)"""
        # Arrange
        create_authenticated_mechanic(client)
        client_data = {
            "name": "Anna",
            "last_name": "Nowak"
        }
        
        # Act
        response = client.post(BASE_URL, json=client_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Anna"
        assert data["last_name"] == "Nowak"
        assert data["phone"] is None
        assert data["pesel"] is None
    
    def test_create_client_with_only_phone(self, client: TestClient):
        """Test tworzenia klienta tylko z telefonem (bez PESEL)"""
        # Arrange
        create_authenticated_mechanic(client)
        
        # Act
        response = client.post(BASE_URL, json={
            "name": "Piotr",
            "last_name": "Wiśniewski",
            "phone": "987654321"
        })
        
        # Assert
        assert response.status_code == 201
        assert response.json()["phone"] == "987654321"
        assert response.json()["pesel"] is None
    
    def test_create_client_with_only_pesel(self, client: TestClient):
        """Test tworzenia klienta tylko z PESEL (bez telefonu)"""
        # Arrange
        create_authenticated_mechanic(client)
        
        # Act
        response = client.post(BASE_URL, json={
            "name": "Maria",
            "last_name": "Dąbrowska",
            "pesel": "98765432109"
        })
        
        # Assert
        assert response.status_code == 201
        assert response.json()["pesel"] == "98765432109"
        assert response.json()["phone"] is None
    
    def test_create_client_formats_names_to_title_case(self, client: TestClient):
        """
        Test automatycznego formatowania imion do Title Case.
        "jan kowalski" → "Jan Kowalski"
        """
        # Arrange
        create_authenticated_mechanic(client)
        
        # Act
        response = client.post(BASE_URL, json={
            "name": "jan",
            "last_name": "kowalski"
        })
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Jan"  # Sformatowane
        assert data["last_name"] == "Kowalski"  # Sformatowane
    
    def test_create_client_trims_whitespace(self, client: TestClient):
        """Test usuwania białych znaków z początku i końca"""
        # Arrange
        create_authenticated_mechanic(client)
        
        # Act
        response = client.post(BASE_URL, json={
            "name": "  Jan  ",
            "last_name": "  Kowalski  "
        })
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Jan"
        assert data["last_name"] == "Kowalski"


# ============================================================================
# TESTY WALIDACJI
# ============================================================================

@pytest.mark.api
@pytest.mark.integration
class TestClientValidation:
    """Testy walidacji danych klienta"""
    
    def test_create_client_missing_name(self, client: TestClient):
        """Test braku wymaganego pola 'name'"""
        # Arrange
        create_authenticated_mechanic(client)
        
        # Act
        response = client.post(BASE_URL, json={
            "last_name": "Kowalski"
        })
        
        # Assert
        assert response.status_code == 422
        assert "name" in response.json()["detail"][0]["loc"]
    
    def test_create_client_missing_last_name(self, client: TestClient):
        """Test braku wymaganego pola 'last_name'"""
        # Arrange
        create_authenticated_mechanic(client)
        
        # Act
        response = client.post(BASE_URL, json={
            "name": "Jan"
        })
        
        # Assert
        assert response.status_code == 422
        assert "last_name" in response.json()["detail"][0]["loc"]
    
    def test_create_client_pesel_too_short(self, client: TestClient):
        """Test PESEL krótszego niż 11 znaków"""
        # Arrange
        create_authenticated_mechanic(client)
        
        # Act
        response = client.post(BASE_URL, json={
            "name": "Jan",
            "last_name": "Kowalski",
            "pesel": "123456789"  # 9 znaków - za krótkie
        })
        
        # Assert
        assert response.status_code == 422
    
    def test_create_client_pesel_too_long(self, client: TestClient):
        """Test PESEL dłuższego niż 11 znaków"""
        # Arrange
        create_authenticated_mechanic(client)
        
        # Act
        response = client.post(BASE_URL, json={
            "name": "Jan",
            "last_name": "Kowalski",
            "pesel": "123456789012"  # 12 znaków - za długie
        })
        
        # Assert
        assert response.status_code == 422
    
    def test_create_client_pesel_exactly_11_chars(self, client: TestClient):
        """Test poprawnego PESEL - dokładnie 11 znaków"""
        # Arrange
        create_authenticated_mechanic(client)
        
        # Act
        response = client.post(BASE_URL, json={
            "name": "Jan",
            "last_name": "Kowalski",
            "pesel": "12345678901"  # Dokładnie 11
        })
        
        # Assert
        assert response.status_code == 201


# ============================================================================
# TESTY DUPLIKATÓW
# ============================================================================

@pytest.mark.api
@pytest.mark.integration
class TestClientDuplicates:
    """Testy sprawdzające duplikaty klientów"""
    
    def test_create_client_duplicate_name_and_last_name(self, client: TestClient):
        """
        GIVEN: Klient "Jan Kowalski" już istnieje
        WHEN: Próba utworzenia drugiego "Jan Kowalski"
        THEN: Status 409 Conflict
        """
        # Arrange
        create_authenticated_mechanic(client)
        
        # Utwórz pierwszego klienta
        create_test_client(client, name="Jan", last_name="Kowalski")
        
        # Act - próba utworzenia drugiego z tym samym imieniem
        response = client.post(BASE_URL, json={
            "name": "Jan",
            "last_name": "Kowalski",
            "phone": "999888777"  # Inny telefon
        })
        
        # Assert
        assert response.status_code == 409
        assert "name and last name already exists" in response.json()["detail"]
    
    def test_create_client_duplicate_name_case_insensitive(self, client: TestClient):
        """
        Test case-insensitive sprawdzania duplikatów.
        "Jan Kowalski" == "jan kowalski" == "JAN KOWALSKI"
        """
        # Arrange
        create_authenticated_mechanic(client)
        create_test_client(client, name="Jan", last_name="Kowalski")
        
        # Act - różna wielkość liter
        response = client.post(BASE_URL, json={
            "name": "JAN",
            "last_name": "KOWALSKI"
        })
        
        # Assert
        assert response.status_code == 409
    
    def test_create_client_duplicate_phone(self, client: TestClient):
        """
        GIVEN: Klient z numerem "123456789" już istnieje
        WHEN: Próba utworzenia klienta z tym samym numerem
        THEN: Status 409 Conflict
        """
        # Arrange
        create_authenticated_mechanic(client)
        create_test_client(client, phone="123456789")
        
        # Act
        response = client.post(BASE_URL, json={
            "name": "Anna",
            "last_name": "Nowak",
            "phone": "123456789"  # Ten sam numer
        })
        
        # Assert
        assert response.status_code == 409
        assert "phone number already exists" in response.json()["detail"]
    
    def test_create_client_duplicate_pesel(self, client: TestClient):
        """
        GIVEN: Klient z PESEL "12345678901" już istnieje
        WHEN: Próba utworzenia klienta z tym samym PESEL
        THEN: Status 409 Conflict
        """
        # Arrange
        create_authenticated_mechanic(client)
        create_test_client(client, pesel="12345678901")
        
        # Act
        response = client.post(BASE_URL, json={
            "name": "Piotr",
            "last_name": "Wiśniewski",
            "pesel": "12345678901"  # Ten sam PESEL
        })
        
        # Assert
        assert response.status_code == 409
        assert "pesel already exists" in response.json()["detail"]
    
    def test_create_multiple_clients_with_null_phone(self, client: TestClient):
        """
        Test: wielu klientów może mieć NULL phone (NULL != NULL w SQL).
        To powinno być dozwolone.
        """
        # Arrange
        create_authenticated_mechanic(client)
        
        # Act - utwórz dwóch klientów bez telefonu
        response1 = client.post(BASE_URL, json={
            "name": "Jan",
            "last_name": "Kowalski"
        })
        response2 = client.post(BASE_URL, json={
            "name": "Anna",
            "last_name": "Nowak"
        })
        
        # Assert
        assert response1.status_code == 201
        assert response2.status_code == 201
    
    def test_create_multiple_clients_with_null_pesel(self, client: TestClient):
        """Test: wielu klientów może mieć NULL pesel"""
        # Arrange
        create_authenticated_mechanic(client)
        
        # Act
        response1 = client.post(BASE_URL, json={
            "name": "Jan",
            "last_name": "Kowalski",
            "phone": "111111111"
        })
        response2 = client.post(BASE_URL, json={
            "name": "Anna",
            "last_name": "Nowak",
            "phone": "222222222"
        })
        
        # Assert
        assert response1.status_code == 201
        assert response2.status_code == 201


# ============================================================================
# TESTY POBIERANIA KLIENTA (READ)
# ============================================================================

@pytest.mark.api
@pytest.mark.integration
class TestGetClient:
    """Tests for GET /api/v1/clients/{client_id} - getting client"""
    
    def test_get_client_success(self, client: TestClient):
        """
        GIVEN: Client exists in the database
        WHEN: GET /clients/{id}
        THEN: Status 200, returned client data
        """
        # Arrange
        create_authenticated_mechanic(client)
        create_response = create_test_client(client)
        client_id = create_response.json()["id"]
        
        # Act
        response = client.get(f"{BASE_URL}/{client_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == client_id
        assert data["name"] == "Jan"
        assert data["last_name"] == "Kowalski"
    
    def test_get_client_not_found(self, client: TestClient):
        """
        GIVEN: Client with ID 99999 does not exist
        WHEN: GET /clients/99999
        THEN: Status 404
        """
        # Arrange
        create_authenticated_mechanic(client)
        
        # Act
        response = client.get(f"{BASE_URL}/99999")
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Client not found"
    
    def test_get_client_returns_decrypted_pesel(self, client: TestClient):
        """
        Test: PESEL is encrypted in the database, but API returns decrypted.
        """
        # Arrange
        create_authenticated_mechanic(client)
        pesel = "98765432109"
        create_response = create_test_client(client, pesel=pesel)
        client_id = create_response.json()["id"]
        
        # Act
        response = client.get(f"{BASE_URL}/{client_id}")
        
        # Assert
        assert response.status_code == 200
        assert response.json()["pesel"] == pesel  # Decrypted


# ============================================================================
# TESTY AKTUALIZACJI KLIENTA (UPDATE)
# ============================================================================

@pytest.mark.api
@pytest.mark.integration
class TestUpdateClient:
    """Tests for PUT /api/v1/clients/{client_id} - updating client"""
    
    def test_update_client_name(self, client: TestClient):
        """Test updating client's name"""
        # Arrange
        create_authenticated_mechanic(client)
        create_response = create_test_client(client, name="Jan")
        client_id = create_response.json()["id"]
        
        # Act
        response = client.put(f"{BASE_URL}/{client_id}", json={
            "name": "Janusz"
        })
        
        # Assert
        assert response.status_code == 200
        assert response.json()["name"] == "Janusz"
        assert response.json()["last_name"] == "Kowalski"  # Not changed
    
    def test_update_client_all_fields(self, client: TestClient):
        """Test updating all fields"""
        # Arrange
        create_authenticated_mechanic(client)
        create_response = create_test_client(client)
        client_id = create_response.json()["id"]
        
        # Act
        response = client.put(f"{BASE_URL}/{client_id}", json={
            "name": "Piotr",
            "last_name": "Wiśniewski",
            "phone": "999888777",
            "pesel": "11111111111"
        })
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Piotr"
        assert data["last_name"] == "Wiśniewski"
        assert data["phone"] == "999888777"
        assert data["pesel"] == "11111111111"
    
    def test_update_client_partial_update(self, client: TestClient):
        """
        Test partial update (PATCH-like behavior).
        Tylko podane pola są aktualizowane.
        """
        # Arrange
        create_authenticated_mechanic(client)
        create_response = create_test_client(
            client,
            name="Jan",
            last_name="Kowalski",
            phone="123456789"
        )
        client_id = create_response.json()["id"]
        
        # Act - update only phone
        response = client.put(f"{BASE_URL}/{client_id}", json={
            "phone": "987654321"
        })
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["phone"] == "987654321"
        assert data["name"] == "Jan"  
        assert data["last_name"] == "Kowalski"  

    def test_update_client_formats_names(self, client: TestClient):
        """Test formatting names during update"""
        # Arrange
        create_authenticated_mechanic(client)
        create_response = create_test_client(client)
        client_id = create_response.json()["id"]
        
        # Act
        response = client.put(f"{BASE_URL}/{client_id}", json={
            "name": "piotr",
            "last_name": "wiśniewski"
        })
        
        # Assert
        assert response.status_code == 200
        assert response.json()["name"] == "Piotr"
        assert response.json()["last_name"] == "Wiśniewski"
    
    def test_update_client_not_found(self, client: TestClient):
        """Test updating non-existent client"""
        # Arrange
        create_authenticated_mechanic(client)
        
        # Act
        response = client.put(f"{BASE_URL}/99999", json={
            "name": "Test"
        })
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Client not found"
    
    def test_update_client_clear_optional_fields(self, client: TestClient):
        """Test clearing optional fields (setting to None)"""
        # Arrange
        create_authenticated_mechanic(client)
        create_response = create_test_client(
            client,
            phone="123456789",
            pesel="12345678901"
        )
        client_id = create_response.json()["id"]
        
        # Act - clear phone
        response = client.put(f"{BASE_URL}/{client_id}", json={
            "phone": None
        })
        
        # Assert
        assert response.status_code == 200
        assert response.json()["phone"] is None
        assert response.json()["pesel"] == "12345678901"  


# ============================================================================
# TESTS FOR DELETING CLIENT (DELETE)
# ============================================================================

@pytest.mark.api
@pytest.mark.integration
class TestDeleteClient:
    """Tests for DELETE /api/v1/clients/{client_id} - deleting client"""
    
    def test_delete_client_success(self, client: TestClient):
        """
        GIVEN: Client exists
        WHEN: DELETE /clients/{id}
        THEN: Status 204, client deleted
        """
        # Arrange
        create_authenticated_mechanic(client)
        create_response = create_test_client(client)
        client_id = create_response.json()["id"]
        
        # Act
        response = client.delete(f"{BASE_URL}/{client_id}")
        
        # Assert
        assert response.status_code == 204
        
        # Check if really deleted
        get_response = client.get(f"{BASE_URL}/{client_id}")
        assert get_response.status_code == 404
    
    def test_delete_client_not_found(self, client: TestClient):
        """Test deleting non-existent client"""
        # Arrange
        create_authenticated_mechanic(client)
        
        # Act
        response = client.delete(f"{BASE_URL}/99999")
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Client not found"
    
    def test_delete_client_idempotent(self, client: TestClient):
        """
        Test: Second deletion of the same client returns 404.
        DELETE is not idempotent in this API (returns 404, not 204).
        """
        # Arrange
        create_authenticated_mechanic(client)
        create_response = create_test_client(client)
        client_id = create_response.json()["id"]
        
        # Act - first deletion
        response1 = client.delete(f"{BASE_URL}/{client_id}")
        # Second deletion
        response2 = client.delete(f"{BASE_URL}/{client_id}")
        
        # Assert
        assert response1.status_code == 204
        assert response2.status_code == 404


# ============================================================================
# TESTS FOR AUTHORIZATION
# ============================================================================

@pytest.mark.api
@pytest.mark.integration
class TestClientAuthorization:
    """Tests for authorization - requires login"""
    
    def test_create_client_without_auth(self, client: TestClient):
        """Test creating client without login"""
        # Act - brak logowania
        response = client.post(BASE_URL, json={
            "name": "Jan",
            "last_name": "Kowalski"
        })
        
        # Assert
        assert response.status_code == 401
        assert response.json()["detail"] == "Token missing"
    
    def test_get_client_without_auth(self, client: TestClient):
        """Test getting client without login"""
        # Act
        response = client.get(f"{BASE_URL}/1")
        
        # Assert
        assert response.status_code == 401
    
    def test_update_client_without_auth(self, client: TestClient):
        """Test updating client without login"""
        # Act
        response = client.put(f"{BASE_URL}/1", json={"name": "Test"})
        
        # Assert
        assert response.status_code == 401
    
    def test_delete_client_without_auth(self, client: TestClient):
        """Test deleting client without login"""
        # Act
        response = client.delete(f"{BASE_URL}/1")
        
        # Assert
        assert response.status_code == 401


# ============================================================================
# TESTS FOR PARAMETRIZED
# ============================================================================

@pytest.mark.api
@pytest.mark.integration
class TestClientParametrized:
    """Tests for different formatting scenarios"""
    
    @pytest.mark.parametrize("name,last_name,expected_name,expected_last_name", [
        ("jan", "kowalski", "Jan", "Kowalski"),
        ("JAN", "KOWALSKI", "Jan", "Kowalski"),
        ("jAn", "kOwAlSkI", "Jan", "Kowalski"),
        ("  jan  ", "  kowalski  ", "Jan", "Kowalski"),
        ("jan maria", "kowalski nowak", "Jan Maria", "Kowalski Nowak"),
    ])
    def test_name_formatting_variations(
        self, client, name, last_name, expected_name, expected_last_name
    ):
        """Test different name formatting variations"""
        # Arrange
        create_authenticated_mechanic(client)
        
        # Act
        response = client.post(BASE_URL, json={
            "name": name,
            "last_name": last_name
        })
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == expected_name
        assert data["last_name"] == expected_last_name
    
    @pytest.mark.parametrize("pesel,expected_status", [
        ("12345678901", 201),      # Poprawny
        ("00000000000", 201),      # Same zera - OK
        ("99999999999", 201),      # Same dziewiątki - OK
        ("1234567890", 422),       # Za krótki
        ("123456789012", 422),     # Za długi
        # Pusty string pomijamy - dla braku PESEL po prostu nie wysyłamy tego pola
    ])
    def test_pesel_validation_cases(self, client, pesel, expected_status):
        """Test different PESEL validation cases"""
        # Arrange
        create_authenticated_mechanic(client)
        
        # Act
        payload = {
            "name": "Test",
            "last_name": "User",
            "pesel": pesel
        }
            
        response = client.post(BASE_URL, json=payload)
        
        # Assert
        assert response.status_code == expected_status


# ============================================================================
# TESTS FOR EDGE CASES
# ============================================================================

@pytest.mark.api
@pytest.mark.integration
class TestClientEdgeCases:
    """Test edge cases"""
    
    def test_create_client_with_very_long_names(self, client: TestClient):
        """Test very long names (check if there is no limit)"""
        # Arrange
        create_authenticated_mechanic(client)
        long_name = "A" * 100
        long_last_name = "B" * 100
        
        # Act
        response = client.post(BASE_URL, json={
            "name": long_name,
            "last_name": long_last_name
        })
        
        # Assert
        assert response.status_code == 201
    
    def test_create_client_with_special_characters_in_names(self, client: TestClient):
        """Test special characters in names"""
        # Arrange
        create_authenticated_mechanic(client)
        
        # Act
        response = client.post(BASE_URL, json={
            "name": "Zoë",
            "last_name": "O'Brien-Smith"
        })
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Zoë"
        assert data["last_name"] == "O'Brien-Smith"
    
    def test_create_client_with_polish_characters(self, client: TestClient):
        """Test Polish characters in names"""
        # Arrange
        create_authenticated_mechanic(client)
        
        # Act
        response = client.post(BASE_URL, json={
            "name": "Józef",
            "last_name": "Wąż-Łęcki"
        })
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Józef"
        assert data["last_name"] == "Wąż-Łęcki"
    
    def test_update_same_values(self, client: TestClient):
        """Test updating to the same values (should work)"""
        # Arrange
        create_authenticated_mechanic(client)
        create_response = create_test_client(client, name="Jan")
        client_id = create_response.json()["id"]
        
        # Act - update to the same value
        response = client.put(f"{BASE_URL}/{client_id}", json={
            "name": "Jan"
        })
        
        # Assert
        assert response.status_code == 200
        assert response.json()["name"] == "Jan"
    
    def test_create_many_clients(self, client: TestClient):
        """Test creating many clients (check performance/scalability)"""
        # Arrange
        create_authenticated_mechanic(client)
        
        # Act - create 10 clients
        created_ids = []
        for i in range(10):
            response = client.post(BASE_URL, json={
                "name": f"Client{i}",
                "last_name": f"Lastname{i}",
                "phone": f"12345678{i:02d}"
            })
            assert response.status_code == 201
            created_ids.append(response.json()["id"])
        
        # Assert - all have unique ID
        assert len(created_ids) == 10
        assert len(set(created_ids)) == 10  
