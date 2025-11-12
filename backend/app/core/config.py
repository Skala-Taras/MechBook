from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    URL_DB: str
    ELASTIC_HOST: str
    jwt_secret_key: str
    algorithm: str
    ENCRYPTION_KEY: str

    FRONTEND_URL: str = "http://localhost:3000"  
    
    # Cookie settings - for production use secure=True, for tests secure=False
    COOKIE_SECURE: bool = True
    COOKIE_SAMESITE: str = "None"  # "None", "Lax", or "Strict"

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool

    class Config:
        env_file = ".env"

settings = Settings()