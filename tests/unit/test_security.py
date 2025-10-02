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
# PASSWORD HASHING TESTS
# ============================================================================

@pytest.mark.unit
class TestPasswordHashing:
    """Tests for password hashing and verification"""
    
    def test_hash_password_returns_different_than_original(self):
        """Password hash should be different than original"""
        password = "my_secret_password"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
    
    def test_same_password_different_hashes(self):
        """Same password should produce different hashes (salt)"""
        password = "password123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2
    
    def test_verify_correct_password(self):
        """Verification of correct password should return True"""
        password = "correct_password"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_wrong_password(self):
        """Verification of wrong password should return False"""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_verify_empty_password(self):
        """Verification of empty password"""
        hashed = hash_password("password123")
        
        assert verify_password("", hashed) is False


# ============================================================================
# JWT TOKEN TESTS
# ============================================================================

@pytest.mark.unit
class TestJWTTokens:
    """Tests for JWT token creation and verification"""
    
    def test_create_access_token(self):
        """JWT token should be a string"""
        data = {"sub": "123", "role": "mechanic"}
        token = create_access_jwt_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        assert token.count('.') == 2  # JWT has 3 parts: header.payload.signature
    
    def test_create_token_with_custom_expiration(self):
        """Token with custom expiration time"""
        data = {"sub": "123"}
        token = create_access_jwt_token(data, expires_delta=timedelta(hours=1))
        
        assert isinstance(token, str)
        # Token should be decodable by jose
        from jose import jwt
        from app.core.config import settings
        
        decoded = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.algorithm])
        assert decoded["sub"] == "123"
        assert "exp" in decoded
    
    def test_create_password_reset_token(self):
        """Password reset token creation"""
        email = "test@example.com"
        token = create_password_reset_token(email)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_password_reset_token_valid(self):
        """Verification of valid password reset token"""
        email = "test@example.com"
        token = create_password_reset_token(email)
        
        result = verify_password_reset_token(token)
        
        assert result is not None
        assert result["email"] == email
        assert "token_id" in result
    
    def test_verify_password_reset_token_invalid(self):
        """Verification of invalid token"""
        result = verify_password_reset_token("invalid.token.here")
        
        assert result is None
    
    def test_verify_password_reset_token_wrong_scope(self):
        """Token with wrong scope should not be accepted"""
        # Create regular access token (without scope="password_reset")
        token = create_access_jwt_token({"sub": "test@example.com"})
        
        result = verify_password_reset_token(token)
        
        assert result is None


# ============================================================================
# ENCRYPTION TESTS
# ============================================================================

@pytest.mark.unit
class TestEncryption:
    """Tests for data encryption and decryption"""
    
    def test_encrypt_data(self):
        """Encryption should return bytes"""
        data = "secret_data"
        encrypted = encrypt_data(data)
        
        assert isinstance(encrypted, bytes)
        assert encrypted != data.encode()
    
    def test_decrypt_data(self):
        """Decryption should return original value"""
        original = "secret_data"
        encrypted = encrypt_data(original)
        decrypted = decrypt_data(encrypted)
        
        assert decrypted == original
    
    def test_encrypt_decrypt_roundtrip(self):
        """Test full cycle: encrypt → decrypt"""
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
        """Encryption of empty string"""
        result = encrypt_data("")
        assert result is None
    
    def test_decrypt_none(self):
        """Decryption of None"""
        result = decrypt_data(None)
        assert result is None


# ============================================================================
# NORMALIZATION TESTS
# ============================================================================

@pytest.mark.unit
class TestNormalization:
    """Tests for data normalization functions"""
    
    def test_normalize_vin_uppercase(self):
        """VIN should be uppercase"""
        vin = "abc123def456"
        normalized = normalize_vin(vin)
        
        assert normalized == "ABC123DEF456"
    
    def test_normalize_vin_removes_spaces(self):
        """VIN should have no spaces"""
        vin = "ABC 123 DEF 456"
        normalized = normalize_vin(vin)
        
        assert normalized == "ABC123DEF456"
    
    def test_normalize_vin_empty(self):
        """Normalization of empty VIN"""
        assert normalize_vin("") == ""
        assert normalize_vin(None) is None
    
    def test_normalize_name_lowercase(self):
        """Name should be lowercase"""
        name = "John DOE"
        normalized = normalize_name(name)
        
        assert normalized == "john doe"
    
    def test_normalize_name_removes_extra_spaces(self):
        """Name should have single spaces"""
        name = "John   Doe    Smith"
        normalized = normalize_name(name)
        
        assert normalized == "john doe smith"
    
    def test_normalize_name_strips_leading_trailing(self):
        """Name should have no leading/trailing spaces"""
        name = "  John Doe  "
        normalized = normalize_name(name)
        
        assert normalized == "john doe"
    
    def test_normalize_name_empty(self):
        """Normalization of empty name"""
        assert normalize_name("") == ""
        assert normalize_name(None) is None


# ============================================================================
# VIN FINGERPRINT TESTS
# ============================================================================

@pytest.mark.unit
class TestVINFingerprint:
    """Tests for VIN fingerprint creation"""
    
    def test_vin_fingerprint_consistent(self):
        """Same VIN should produce same fingerprint"""
        vin = "ABC123DEF456"
        fp1 = vin_fingerprint(vin)
        fp2 = vin_fingerprint(vin)
        
        assert fp1 == fp2
    
    def test_vin_fingerprint_case_insensitive(self):
        """Fingerprint should be case-insensitive"""
        vin_upper = "ABC123DEF456"
        vin_lower = "abc123def456"
        
        fp1 = vin_fingerprint(vin_upper)
        fp2 = vin_fingerprint(vin_lower)
        
        assert fp1 == fp2
    
    def test_vin_fingerprint_ignores_spaces(self):
        """Fingerprint should ignore spaces"""
        vin1 = "ABC123DEF456"
        vin2 = "ABC 123 DEF 456"
        
        fp1 = vin_fingerprint(vin1)
        fp2 = vin_fingerprint(vin2)
        
        assert fp1 == fp2
    
    def test_vin_fingerprint_different_vins(self):
        """Different VINs should produce different fingerprints"""
        vin1 = "ABC123DEF456"
        vin2 = "XYZ789GHI012"
        
        fp1 = vin_fingerprint(vin1)
        fp2 = vin_fingerprint(vin2)
        
        assert fp1 != fp2
    
    def test_vin_fingerprint_empty(self):
        """Fingerprint of empty VIN"""
        assert vin_fingerprint("") is None
        assert vin_fingerprint(None) is None
    
    def test_vin_fingerprint_is_hash(self):
        """Fingerprint should be a hexadecimal hash"""
        vin = "ABC123DEF456"
        fp = vin_fingerprint(vin)
        
        assert isinstance(fp, str)
        assert len(fp) == 64  # SHA256 hex = 64 characters
        assert all(c in '0123456789abcdef' for c in fp)


# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================

@pytest.mark.unit
class TestParametrized:
    """Parametrized tests for various cases"""
    
    @pytest.mark.parametrize("password", [
        "short",
        "medium_password",
        "very_long_password_with_many_characters_12345",
        "with spaces and !@#$%",
        "ąćęłńóśźż",
    ])
    def test_password_hash_verify_various(self, password):
        """Test hashing various passwords"""
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
        """Test various VIN normalization cases"""
        assert normalize_vin(vin) == expected
    
    @pytest.mark.parametrize("name,expected", [
        ("John Doe", "john doe"),
        ("  John   Doe  ", "john doe"),
        ("JOHN DOE", "john doe"),
        ("john doe", "john doe"),
    ])
    def test_normalize_name_cases(self, name, expected):
        """Test various name normalization cases"""
        assert normalize_name(name) == expected

