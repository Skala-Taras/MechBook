"""
Testy jednostkowe dla modułu app.core.security.

Testuje:
- Hashowanie i weryfikacja haseł
- Tworzenie i weryfikacja tokenów JWT
- Szyfrowanie/deszyfrowanie danych
- Normalizacja VIN i nazw
"""
import pytest
from datetime import timedelta

from app.core.security import (
    hash_password,
    verify_password,
    create_access_jwt_token,
    encrypt_data,
    decrypt_data,
    normalize_vin,
    normalize_name,
    vin_fingerprint,
    create_password_reset_token,
    verify_password_reset_token
)


# ============================================================================
# TESTY HASHOWANIA HASEŁ
# ============================================================================

@pytest.mark.unit
class TestPasswordHashing:
    """Testy hashowania i weryfikacji haseł"""
    
    def test_hash_password_returns_different_than_original(self):
        """Hash hasła powinien być inny niż oryginał"""
        password = "my_secret_password"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
    
    def test_same_password_different_hashes(self):
        """To samo hasło powinno dawać różne hashe (salt)"""
        password = "password123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2
    
    def test_verify_correct_password(self):
        """Weryfikacja poprawnego hasła powinna zwrócić True"""
        password = "correct_password"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_wrong_password(self):
        """Weryfikacja błędnego hasła powinna zwrócić False"""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_verify_empty_password(self):
        """Weryfikacja pustego hasła"""
        hashed = hash_password("password123")
        
        assert verify_password("", hashed) is False


# ============================================================================
# TESTY TOKENÓW JWT
# ============================================================================

@pytest.mark.unit
class TestJWTTokens:
    """Testy tworzenia i weryfikacji tokenów JWT"""
    
    def test_create_access_token(self):
        """Token JWT powinien być string'iem"""
        data = {"sub": "123", "role": "mechanic"}
        token = create_access_jwt_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        assert token.count('.') == 2  # JWT ma 3 części: header.payload.signature
    
    def test_create_token_with_custom_expiration(self):
        """Token z niestandardowym czasem wygaśnięcia"""
        data = {"sub": "123"}
        token = create_access_jwt_token(data, expires_delta=timedelta(hours=1))
        
        assert isinstance(token, str)
        # Token powinien być dekodowalny przez jose
        from jose import jwt
        from app.core.config import settings
        
        decoded = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.algorithm])
        assert decoded["sub"] == "123"
        assert "exp" in decoded
    
    def test_create_password_reset_token(self):
        """Token resetowania hasła"""
        email = "test@example.com"
        token = create_password_reset_token(email)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_password_reset_token_valid(self):
        """Weryfikacja poprawnego tokenu resetowania hasła"""
        email = "test@example.com"
        token = create_password_reset_token(email)
        
        result = verify_password_reset_token(token)
        
        assert result is not None
        assert result["email"] == email
        assert "token_id" in result
    
    def test_verify_password_reset_token_invalid(self):
        """Weryfikacja niepoprawnego tokenu"""
        result = verify_password_reset_token("invalid.token.here")
        
        assert result is None
    
    def test_verify_password_reset_token_wrong_scope(self):
        """Token z niewłaściwym scope nie powinien być zaakceptowany"""
        # Utwórz zwykły access token (bez scope="password_reset")
        token = create_access_jwt_token({"sub": "test@example.com"})
        
        result = verify_password_reset_token(token)
        
        assert result is None


# ============================================================================
# TESTY SZYFROWANIA
# ============================================================================

@pytest.mark.unit
class TestEncryption:
    """Testy szyfrowania i deszyfrowania danych"""
    
    def test_encrypt_data(self):
        """Szyfrowanie powinno zwrócić bytes"""
        data = "secret_data"
        encrypted = encrypt_data(data)
        
        assert isinstance(encrypted, bytes)
        assert encrypted != data.encode()
    
    def test_decrypt_data(self):
        """Deszyfrowanie powinno zwrócić oryginalną wartość"""
        original = "secret_data"
        encrypted = encrypt_data(original)
        decrypted = decrypt_data(encrypted)
        
        assert decrypted == original
    
    def test_encrypt_decrypt_roundtrip(self):
        """Test pełnego cyklu: szyfruj → deszyfruj"""
        test_cases = [
            "simple text",
            "text with spaces and 123 numbers",
            "special chars: !@#$%^&*()",
            "Polish: ąćęłńóśźż",
        ]
        
        for original in test_cases:
            encrypted = encrypt_data(original)
            decrypted = decrypt_data(encrypted)
            assert decrypted == original, f"Failed for: {original}"
    
    def test_encrypt_empty_string(self):
        """Szyfrowanie pustego stringa"""
        result = encrypt_data("")
        assert result is None
    
    def test_decrypt_none(self):
        """Deszyfrowanie None"""
        result = decrypt_data(None)
        assert result is None


# ============================================================================
# TESTY NORMALIZACJI
# ============================================================================

@pytest.mark.unit
class TestNormalization:
    """Testy funkcji normalizujących dane"""
    
    def test_normalize_vin_uppercase(self):
        """VIN powinien być uppercase"""
        vin = "abc123def456"
        normalized = normalize_vin(vin)
        
        assert normalized == "ABC123DEF456"
    
    def test_normalize_vin_removes_spaces(self):
        """VIN powinien nie mieć spacji"""
        vin = "ABC 123 DEF 456"
        normalized = normalize_vin(vin)
        
        assert normalized == "ABC123DEF456"
    
    def test_normalize_vin_empty(self):
        """Normalizacja pustego VIN"""
        assert normalize_vin("") == ""
        assert normalize_vin(None) is None
    
    def test_normalize_name_lowercase(self):
        """Nazwa powinna być lowercase"""
        name = "John DOE"
        normalized = normalize_name(name)
        
        assert normalized == "john doe"
    
    def test_normalize_name_removes_extra_spaces(self):
        """Nazwa powinna mieć pojedyncze spacje"""
        name = "John   Doe    Smith"
        normalized = normalize_name(name)
        
        assert normalized == "john doe smith"
    
    def test_normalize_name_strips_leading_trailing(self):
        """Nazwa powinna być bez spacji na początku/końcu"""
        name = "  John Doe  "
        normalized = normalize_name(name)
        
        assert normalized == "john doe"
    
    def test_normalize_name_empty(self):
        """Normalizacja pustego imienia"""
        assert normalize_name("") == ""
        assert normalize_name(None) is None


# ============================================================================
# TESTY VIN FINGERPRINT
# ============================================================================

@pytest.mark.unit
class TestVINFingerprint:
    """Testy tworzenia fingerprint VIN"""
    
    def test_vin_fingerprint_consistent(self):
        """Ten sam VIN powinien dawać ten sam fingerprint"""
        vin = "ABC123DEF456"
        fp1 = vin_fingerprint(vin)
        fp2 = vin_fingerprint(vin)
        
        assert fp1 == fp2
    
    def test_vin_fingerprint_case_insensitive(self):
        """Fingerprint powinien być niezależny od wielkości liter"""
        vin_upper = "ABC123DEF456"
        vin_lower = "abc123def456"
        
        fp1 = vin_fingerprint(vin_upper)
        fp2 = vin_fingerprint(vin_lower)
        
        assert fp1 == fp2
    
    def test_vin_fingerprint_ignores_spaces(self):
        """Fingerprint powinien ignorować spacje"""
        vin1 = "ABC123DEF456"
        vin2 = "ABC 123 DEF 456"
        
        fp1 = vin_fingerprint(vin1)
        fp2 = vin_fingerprint(vin2)
        
        assert fp1 == fp2
    
    def test_vin_fingerprint_different_vins(self):
        """Różne VIN-y powinny dawać różne fingerprint'y"""
        vin1 = "ABC123DEF456"
        vin2 = "XYZ789GHI012"
        
        fp1 = vin_fingerprint(vin1)
        fp2 = vin_fingerprint(vin2)
        
        assert fp1 != fp2
    
    def test_vin_fingerprint_empty(self):
        """Fingerprint pustego VIN"""
        assert vin_fingerprint("") is None
        assert vin_fingerprint(None) is None
    
    def test_vin_fingerprint_is_hash(self):
        """Fingerprint powinien być hexadecymalnym hashem"""
        vin = "ABC123DEF456"
        fp = vin_fingerprint(vin)
        
        assert isinstance(fp, str)
        assert len(fp) == 64  # SHA256 hex = 64 znaki
        assert all(c in '0123456789abcdef' for c in fp)


# ============================================================================
# TESTY PARAMETRYZOWANE
# ============================================================================

@pytest.mark.unit
class TestParametrized:
    """Testy parametryzowane dla różnych przypadków"""
    
    @pytest.mark.parametrize("password", [
        "short",
        "medium_password",
        "very_long_password_with_many_characters_12345",
        "with spaces and !@#$%",
        "ąćęłńóśźż",
    ])
    def test_password_hash_verify_various(self, password):
        """Test hashowania różnych haseł"""
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
        assert verify_password(password + "x", hashed) is False
    
    @pytest.mark.parametrize("vin,expected", [
        ("abc123", "ABC123"),
        ("  abc  123  ", "ABC123"),
        ("ABC123", "ABC123"),
        ("aBc 123", "ABC123"),
    ])
    def test_normalize_vin_cases(self, vin, expected):
        """Test różnych przypadków normalizacji VIN"""
        assert normalize_vin(vin) == expected
    
    @pytest.mark.parametrize("name,expected", [
        ("John Doe", "john doe"),
        ("  John   Doe  ", "john doe"),
        ("JOHN DOE", "john doe"),
        ("john doe", "john doe"),
    ])
    def test_normalize_name_cases(self, name, expected):
        """Test różnych przypadków normalizacji nazw"""
        assert normalize_name(name) == expected

