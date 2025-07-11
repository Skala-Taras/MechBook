import os
from datetime import datetime, timedelta
from app.core.config import settings
from jose import jwt
from passlib.context import CryptContext

from app.schemas.token import Token

pwd_context = CryptContext(schemes=["sha256_crypt"])


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(pw_to_verify:str, hashed_pw: str) -> bool:
    return pwd_context.verify(pw_to_verify, hashed_pw)

def create_access_jwt_token(data: dict, expires_delta: timedelta=timedelta(minutes=1)):
    to_code = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_code.update({"exp": expire})
    return jwt.encode(to_code, settings.jwt_secret_key, algorithm=settings.algorithm)

