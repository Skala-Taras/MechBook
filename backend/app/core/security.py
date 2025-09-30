from datetime import datetime, timedelta
from app.core.config import settings
from jose import jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from sqlalchemy.types import TypeDecorator, LargeBinary
import hmac
import hashlib
import uuid

# Initialize Fernet with the encryption key from your .env file
# This key is used for both encrypting and decrypting.
fernet = Fernet(settings.ENCRYPTION_KEY.encode())

pwd_context = CryptContext(schemes=["sha256_crypt"])


def encrypt_data(data: str) -> bytes:
    """Encrypts a plain-text string into bytes."""
    if not data:
        return None
    return fernet.encrypt(data.encode())


def decrypt_data(encrypted_data: bytes) -> str:
    """Decrypts bytes back into a plain-text string."""
    if not encrypted_data:
        return None
    return fernet.decrypt(encrypted_data).decode()


class EncryptedType(TypeDecorator):
    """
    This is the core of the automatic encryption.
    It's a custom SQLAlchemy type that hooks into the database read/write process.
    """
    impl = LargeBinary

    def process_bind_param(self, value, dialect):
        """
        This function is AUTOMATICALLY called by SQLAlchemy just before saving data to the database.
        It takes the plain-text value (like a VIN) and encrypts it.
        """
        if value is not None:
            print(f"ENCRYPTING: Original value: '{value}'")
            encrypted_value = encrypt_data(str(value))
            print(f"ENCRYPTING: Encrypted value: {encrypted_value}")
            return encrypted_value
        return None

    def process_result_value(self, value, dialect):
        """
        This function is AUTOMATICALLY called by SQLAlchemy just after reading data from the database.
        It takes the encrypted value from the DB and decrypts it back to plain text.
        """
        if value is not None:
            print(f"DECRYPTING: Encrypted value from DB: {value}")
            decrypted_value = decrypt_data(value)
            print(f"DECRYPTING: Decrypted to: '{decrypted_value}'")
            return decrypted_value
        return None


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(pw_to_verify:str, hashed_pw: str) -> bool:
    return pwd_context.verify(pw_to_verify, hashed_pw)


def create_access_jwt_token(data: dict, expires_delta: timedelta = timedelta(days=7)):
    to_code = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_code.update({"exp": expire})
    return jwt.encode(to_code, settings.jwt_secret_key, algorithm=settings.algorithm)

def create_password_reset_token(email: str) -> str:
    """Creates a unique token for password reset with one-time use tracking."""
    # Create unique token ID
    token_id = str(uuid.uuid4())
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode = {"exp": expire, "sub": email, "scope": "password_reset", "jti": token_id}
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.algorithm)

def verify_password_reset_token(token: str) -> dict | None:
    """Verifies the password reset token and returns email and token ID."""
    try:
        decoded_token = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.algorithm])
        if decoded_token.get("scope") == "password_reset":
            return {
                "email": decoded_token.get("sub"),
                "token_id": decoded_token.get("jti")
            }
    except jwt.JWTError:
        return None
    return None


def normalize_vin(vin: str) -> str:
    """Normalize VIN: uppercase, no spaces"""
    if not vin:
        return vin
    return "".join(vin.split()).upper()


def normalize_name(name: str) -> str:
    """Normalize name: lowercase, no extra spaces"""
    if not name:
        return name
    return " ".join(name.strip().split()).lower()


def vin_fingerprint(vin: str) -> str:
    """Create a secure fingerprint of VIN for duplicate detection"""
    if not vin:
        return None
    normalized = normalize_vin(vin)
    return hmac.new(
        settings.ENCRYPTION_KEY.encode(),
        normalized.encode(),
        hashlib.sha256
    ).hexdigest()

